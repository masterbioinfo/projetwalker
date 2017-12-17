""" Titration class module

Titration allows manipulating chemical shift data measured with 2D NMR
Input is a set of `.list` tabular files with one residue per line, e.g output of Sparky
It calculates chemical shift variation at each titration step using the first step as reference.
They are transformed into a single 'intensity' value, associated to a residue.
The class provides matplotlib wrapping functions, allowing to display the data from the analysis,
as well as setting a cut-off to filter residues having high intensity values.
"""

import os
import glob
import pickle
import re
import sys
import csv
import json
import yaml
from collections import OrderedDict
from math import *

import pandas as pd

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FormatStrFormatter

from classes.AminoAcid import AminoAcid
from classes.plots import Hist, MultiHist, ShiftMap, SplitShiftMap, TitrationCurve
from classes.widgets import CutOffCursor


## --------------------------------------------------------------------
##      Import modules settings
## --------------------------------------------------------------------

represent_dict_order = lambda self, data: self.represent_mapping('tag:yaml.org,2002:map', data.items())
""" setup YAML for ordered dict output : https://stackoverflow.com/a/8661021 """
yaml.add_representer(OrderedDict, represent_dict_order)

# Setup pandas float precision
pd.set_option('precision', 3)


## --------------------------------------------------------------------
##      Shift2Me classes
## --------------------------------------------------------------------

class BaseTitration(object):

    INIT_FIELDS=('name', 'analyte', 'titrant', 'start_volume', 'add_volumes')
    COLUMN_ALIASES = ('step',  'vol_add', 'vol_titrant', 'vol_total', 'conc_titrant', 'conc_analyte', 'ratio')

    def __init__(self, initStream=None, **kwargs):

        self.isInit = False
        self.steps = 1
        self.titrant = {
            "name" : 'titrant',
            "concentration" : 0
        }
        self.analyte = {
            "name" : 'analyte',
            'concentration' : 0
        }

        self.startVol = 0
        self.analyteStartVol = 0

        self.volumes = [0]

        if initStream is not None: # init from file
            self.load_init_file(initStream)
        elif kwargs: # init from dict
            self.load_init_dict(kwargs)

## ----------------------------------------------------------
##      Protocole using pandas
## ----------------------------------------------------------
## ----------------------------------------------------------
    @property
    def protocole(self):
        return self.make_protocole()

    def make_protocole(self, index=True):
        self._protocole = pd.DataFrame(index=list(range(self.steps)) or [0], columns=self.COLUMN_ALIASES, data=0)
        self.update_protocole()
        self.set_protocole_headers()
        if index:
            self._protocole.set_index('Step', inplace=True)
        return self._protocole


    def update_protocole(self):
        self._protocole['step'] = list(range(self.steps))
        self._protocole['vol_add'] = self.volumes
        self._protocole['vol_titrant'] = self._protocole['vol_add'].cumsum()
        self._protocole['vol_total'] = self.startVol + self._protocole['vol_titrant']
        self._protocole['conc_titrant'] = self._protocole['vol_titrant'] * self.titrant['concentration'] / self._protocole['vol_total']
        self._protocole['conc_analyte'] = self.analyteStartVol * self.analyte['concentration'] / self._protocole['vol_total']
        self._protocole['ratio'] = self._protocole['conc_titrant'] / self._protocole['conc_analyte']

    def set_protocole_headers(self):
        headers = list(map(
            lambda s: s.format(
                titrant=self.titrant['name'],
                analyte=self.analyte['name']),
            [
                'Step',
                'Added {titrant} (µL)',
                'Total {titrant} (µL)',
                'Total volume (µL)',
                '[{titrant}] (µM)',
                '[{analyte}] (µM)',
                '[{titrant}]/[{analyte}]'
            ]))
        self._protocole.columns = list(headers)

## -----------------------------------------------------
##         Input/output
## -----------------------------------------------------

    @staticmethod
    def extract_init_file(dirPath):
        initFileList = glob.glob(os.path.join(dirPath, '*.yml')) or glob.glob(os.path.join(dirPath,'*.json'))
        if len(initFileList) > 1:
            initFile = min(initFileList, key=os.path.getctime)
            print("{number} init files found in {source}. Using most recent one : {file}".format(
                                number=len(initFileList), source=dirPath, file=initFile ),
                                file=sys.stderr)
        elif initFileList:
            initFile = initFileList.pop()
        else:
            initFile = None
        return initFile

    def validate(self):
        valid = True

        if not self.titrant['name']:
            self.titrant['name'] = 'titrant'
        if not self.analyte['name']:
            self.analyte['name'] = 'analyte'

        if self.titrant['concentration'] <= 0:
            self.titrant['concentration'] = 0
            valid = False

        if self.analyte['concentration'] <= 0:
            self.analyte['concentration'] = 0
            valid = False

        if self.startVol <= 0:
            self.startVol = 0
            valid=False
        if self.analyteStartVol <= 0:
            self.analyteStartVol = 0
            valid=False
        if self.analyteStartVol >= self.startVol:
            valid=False

        if self.volumes[0] != 0:
            valid=False

        return valid


    @staticmethod
    def validate_init_dict(initDict):
        try:
            for role in ['titrant', 'analyte']:
                concentration = float(initDict[role]['concentration'])
                if concentration <=0:
                    raise ValueError("Invalid concentration ({conc}) for {role}".format(conc=concentration, role=role))

            volAnalyte = float(initDict['start_volume']['analyte'])
            volTotal = float(initDict['start_volume']['total'])
            for volume in (volAnalyte, volTotal):
                if volume <= 0:
                    raise ValueError("Invalid volume ({vol}) for {volKey}".format(vol=volume, volKey=volumeKey))
            if  volAnalyte > volTotal:
                raise ValueError("Initial analyte volume ({analyte}) cannot be greater than total volume {total}".format(analyte=volAnalyte, total=volTotal))
            return initDict
        except TypeError as typeError:
            typeError.args = ("Could not convert value to number : {error}".format(error=typeError), )
            raise
        except KeyError as keyError:
            keyError.args = ("Missing required data for protocole initialization. Hint: {error}".format(error=keyError), )
            raise

    def load_init_path(self, initFile):
        loaders = {
            '.yml' : yaml,
            '.json' : json
        }
        root, ext = os.path.splitext(initFile)

        loader = loaders.get(ext)
        if loader is None:
            raise IOError("Invalid init file extension for {init} : accepted are .yml or .json".format(init=initFile))

        try:
            with open(initFile, 'r') as initStream:
                self.load_init_file(initStream, loader)
        except IOError as error:
            raise
            return

        print("[Protocole]\tLoading protocole parameters from {initFile}".format(
            initFile=initFile),
            file=sys.stderr)

    def load_init_file(self, initStream, loader=yaml):
        try:
            initDict = loader.load(initStream)
            if initDict:
                self.load_init_dict(initDict)
            return self.isInit
        except IOError as fileError:
            raise
        except (ValueError,yaml.YAMLError) as valError:
            valError.args = ("Error : {error}".format(error=valError), )
            raise

    def load_init_dict(self, initDict):
        initDict = self.validate_init_dict(initDict)
        if initDict is None:
            return

        #set name
        self.name = self.set_name(initDict.get('name'))

        self.titrant = initDict['titrant']
        self.analyte = initDict['analyte']
        for initConcentration in (self.titrant, self.analyte):
            initConcentration['concentration'] = float(initConcentration['concentration'])

        self.analyteStartVol = float(initDict['start_volume']['analyte'])
        self.startVol = float(initDict['start_volume']['total'])
        self.set_volumes(initDict.get('add_volumes', self.volumes))
        self.isInit = self.validate()
        return self.isInit

    def dump_init_file(self, initFile=None):
        try:
            fh = open(initFile, 'w') if initFile else sys.stdout
            yaml.dump(self.as_init_dict, fh, default_flow_style=False, indent=4)
            if fh is not sys.stdout:
                fh.close()
            return initFile
        except IOError as fileError:
            print("{error}".format(error=fileError), file=sys.stderr)
            return



## -------------------------------------------------
##         Manipulation methods
## -------------------------------------------------
    def set_name(self, name=None):
        "Sets Titration instance name"
        self.name = str(name) if name is not None else self.name or "Unnamed Titration"
        return self.name

    def add_volume(self, volume):
        "Add a volume for next protocole step"
        self.steps += 1
        self.volumes.append(volume)
        return self.steps

    def set_volumes(self, volumes):
        "Set tiration volumes, updating steps to match number of volumes"
        self.steps = len(volumes)
        self.volumes = list(map(float, volumes))

    def update_volumes(self, stepVolumes):
        "Updates protocole volume from a dict \{step_nb: volume\}"
        try:
            for step, vol in stepVolumes.items():
                self.volumes[step] = vol
        except IndexError:
            print("{step} does not exist".format(step=step), file=sys.stderr)

    def add_volumes(self, volumes):
        "Add a list of volumes for next protocole steps"
        for vol in volumes:
            self.add_volume(vol)
        return self.steps

## -----------------------------------------------------
##         Properties
## -----------------------------------------------------


    @property
    def is_consistent(self):
        return True if len(self.volumes) == self.steps else False

    @property
    def as_init_dict(self):
        initDict=OrderedDict({"_description" : "This file defines a titration's initial parameters."})
        unordered = {
            'name' : self.name,
            'titrant' : self.titrant,
            'analyte' : self.analyte,
            'start_volume': {
                "analyte" : self.analyteStartVol,
                "total" : self.startVol
            },
            'add_volumes': self.volumes
        }
        initDict.update([ (field, unordered[field]) for field in self.INIT_FIELDS])
        return initDict


##----------------------------------------------------------------------------------------------------------
##         Classe titration
##----------------------------------------------------------------------------------------------------------

class Titration(BaseTitration):
    """
    Class Titration.
    Contains a list of aminoacid objects
    Provides methods for accessing each titration step datas.
    """
    # accepted file path pattern
    PATH_PATTERN = re.compile(r'(.+/)?(.*[^\d]+)(?P<step>[0-9]+)\.list')
    # accepted lines pattern
    LINE_PATTERN = re.compile(r'^(?P<position>\d+)(\S*)?\s+'
                            r'(?P<chemshiftH>\d+\.\d+)\s+'
                            r'(?P<chemshiftN>\d+\.\d+)$')
    # ignored lines pattern
    IGNORE_LINE_PATTERN = re.compile(r"^\d.*")


    def __init__(self, name=None, cutoff=None, **kwargs):
        """
        Load titration files, check their integrity
        `source` is either a directory containing `.list` file, or is a list of `.list` files
        Separate complete vs incomplete data
        """

        BaseTitration.__init__(self, **kwargs)

        self.name = ""

        self.residues = dict() # all residues {position:AminoAcid object}
        self.complete = dict() # complete data residues
        self.incomplete = dict() # incomplete data residues
        self.selected = dict() # selected residues
        self.intensities = list() # 2D array of intensities

        self.dataSteps = 0
        self.cutoff = None

        self.files = []

        #BaseTitration.__init__(self)

        ## FILE PATH PROCESSING
        # fetch all .list files in source dir, parse
        # add a step for each file

        ## INIT CUTOFF
        if cutoff:
            self.set_cutoff(cutoff)

        ## finish
        self.name = self.name or "Unnamed Titration"


## ---------------------------------------------
##      Titration + RMN Analysis
## ---------------------------------------------

    def set_sequence(self, sequence, offset=0):
        raise NotImplementedError

    def add_step(self, fileName, titrationStream, volume=None):
        "Adds a titration step described in `titrationFile`"
        print("[Step {step}]\tLoading NMR data from {titration_file}".format(
            step=self.dataSteps, titration_file=fileName),
            file=sys.stderr)

        # verify file
        step = self.validate_filepath(fileName, verifyStep=True)
        # parse it
        try:
            self.parse_titration_file(titrationStream)
        except ValueError as parseError:
            print("{error} in file {file}.".format(
                error=parseError, file=fileName),
                file=sys.stderr)
            return

        self.dataSteps += 1
        self.files.append(fileName)

        if volume is not None:
            if self.steps < self.dataSteps:
                super().add_volume(volume)
            else:
                super().update_volumes({step:volume})


        # create residues with no data for missing positions
        for pos in range(min(self.residues), max(self.residues)):
            if pos not in self.residues:
                self.residues.update({pos: AminoAcid(position=pos)})

        # reset complete residues and update
        self.complete = dict()
        for pos, res in self.residues.items():
            if res.validate(self.dataSteps):
                self.complete.update({pos:res})
            else:
                self.incomplete.update({pos:res})

        print("\t\t{incomplete} incomplete residue out of {total}".format(
             incomplete=len(self.incomplete), total=len(self.complete)),
             file=sys.stderr)

        # Recalculate (position, chem shift intensity) coordinates for histogram plot
        self.intensities = [] # 2D array, by titration step then residu position
        for step in range(self.dataSteps): # intensity is null for reference step, ignoring
            self.intensities.append([residue.chemshiftIntensity[step] for residue in self.complete.values()])

    def set_cutoff(self, cutoff):
        "Sets cut off for all titration steps"
        raise NotImplementedError

    def validate_filepath(self, filePath, verifyStep=False):
        """
        Given a file path, checks if it has `.list` extension and if it is numbered after the titration step.
        If `step` arg is provided, validation will enforce that parsed file number matches `step`.
        Returns the titration step number if found, IOError is raised otherwise
        """
        matching = self.PATH_PATTERN.match(filePath) # attempt to match
        if matching:
            if verifyStep and int(matching.group("step")) != self.dataSteps:
                raise IOError("File {file} expected to contain data for titration step #{step}."
                                "Are you sure this is the file you want ?"
                                "In this case it must be named like (name){step}.list".format(
                                    file=filePath, step=self.dataSteps))
            # retrieve titration step number parsed from file name
            return int(matching.group("step"))
        else:
            # found incorrect line format
            raise IOError("Refusing to parse file {file}.\nPlease check it is named like (name)(step).list".format(
                file=filePath))

    def parse_titration_file(self, stream):
        """
        Titration file parser.
        Returns a new dict which keys are residues' position and values are AminoAcid objects.
        If residues argument is provided, updates AminoAcid by adding parsed chemical shift values.
        Throws ValueError if incorrect lines are encountered in file.
        """
        for lineNb, line in enumerate(stream) :
            try:
                chemshifts = self.parse_line(line)
                if chemshifts is not None:
                    self.add_chemshifts(chemshifts)
            except ValueError as parseError:
                parseError.args = ("{error} at line {line}".format(
                    error=parseError, line=lineNb), )
                raise
                continue

    def parse_line(self, line):
        "Parses a line from titration file, returning a dictionnaryof parsed data"
        line = line.strip()
        # ignore empty lines and header lines
        if self.IGNORE_LINE_PATTERN.match(line):
            # attempt to match to expected format
            match = self.LINE_PATTERN.match(line)
            if match: # parse as dict
                chemshifts = match.groupdict()
                # Convert parsed str to number types
                for castFunc, key in zip((float, float, int), sorted(chemshifts)):
                    chemshifts[key] = castFunc(chemshifts[key])
                # add or update residue
                return chemshifts
            else:
                # non parsable, non ignorable line
                raise ValueError("Found unparsable line")

    def add_chemshifts(self, chemshifts):
        "Arg chemshifts is a dict with keys position, chemshiftH, chemshiftN"
        position = chemshifts["position"]
        if self.residues.get(position):
            # update AminoAcid object in residues dict
            self.residues[position].add_chemshifts(**chemshifts)
        else:
            # create AminoAcid object in residues dict
            self.residues[position] = AminoAcid(**chemshifts)
        return self.residues[position]




## -------------------------
##    Utils
## -------------------------

    def select_residues(self, *positions):
        "Select a subset of residues"
        for pos in positions:
            try:
                self.selected[pos] = self.residues[pos]
            except KeyError:
                print("Residue at position {pos} does not exist. Skipping selection.".format(pos=pos), file=sys.stderr)
                continue
        return self.selected


    def deselect_residues(self, *positions):
        "Deselect some residues. Calling with no arguments will deselect all."
        try:
            if not positions:
                self.selected = dict()
            else:
                for pos in positions:
                    self.selected.pop(pos)
            return self.selected
        except KeyError:
            pass


## --------------------------
##    Properties
## --------------------------

    @property
    def filtered(self):
        "Returns list of filtered residue having last intensity >= cutoff value"
        if self.cutoff is not None:
            return dict([(res.position, res) for res in self.complete.values() if res.chemshiftIntensity[-1] >= self.cutoff])
        else:
            return dict()

    @property
    def sortedSteps(self):
        """
        Sorted list of titration steps, beginning at step 1.
        Reference step 0 is ignored.
        """
        return list(range(1,self.dataSteps))

    @property
    def added(self):
        return self.volumes[:self.dataSteps] if len(volumes) >= self.dataSteps else self.volumes


class TitrationCLI(Titration):

    def __init__(self, working_directory, name=None, cutoff=None, initFile=None, **kwargs):

        if not os.path.isdir(working_directory):
            raise IOError("{dir} does not exist")
            exit(1)

        self.dirPath = working_directory

        Titration.__init__(self, name=name, **kwargs)

        # init plots
        self.stackedHist = None
        self.hist = dict()
        ## FILE PATH PROCESSING
        # fetch all .list files in source dir, parse
        # add a step for each file
        try:
            self.update()
        except IOError as error:
            print("{error}".format(error=error), file=sys.stderr)
            exit(1)

        initFile = initFile or self.extract_init_file(self.dirPath)

        if initFile: self.load_init_path(initFile)

        if cutoff:
            self.set_cutoff(cutoff)


    def add_step(self, titrationFilePath, volume=None):
        try:
            with open(titrationFilePath, 'r') as titrationStream:
                Titration.add_step(self, titrationFilePath, titrationStream, volume=volume)

            # generate colors for each titration step
            self.colors = plt.cm.get_cmap('hsv', self.dataSteps)

            # close stale stacked hist
            if self.stackedHist and not self.stackedHist.closed:
                self.stackedHist.close()

        except IOError as fileError:
            print("{error}".format(error=fileError), file=sys.stderr)
            return


    def set_cutoff(self, cutoff):
        "Sets cut off for all titration steps"
        try:
            # check cut off validity and store it
            cutoff = float(cutoff)
            self.cutoff = cutoff
            # update cutoff in open hists
            for hist in self.hist.values():
                hist.set_cutoff(cutoff)
            if self.stackedHist:
                self.stackedHist.set_cutoff(cutoff)
            return self.cutoff
        except TypeError as err:
            print("Invalid cut-off value : {error}".format(
                error=err), file=sys.stderr)
            return self.cutoff

## -------------------------
##    Utils
## -------------------------

    def extract_dir(self, directory = None):
        extract_dir = directory or self.dirPath
        if not ( extract_dir and os.path.isdir(extract_dir)): return []

        extract_dir = os.path.abspath(extract_dir)

        # update protocole if init file is present
        initFile = self.extract_init_file(extract_dir)
        if initFile:
            with open(initFile, 'r') as initStream:
                self.load_init_file(initStream)

        files = set(glob.glob(os.path.join(extract_dir, '*.list')))
        if len(files) < 1:
            raise ValueError("Directory {dir} does not contain any `.list` titration file.".format(
                dir=extract_dir))
        return files

    def extract_source(self, source=None):
        """
        Handles source data depending on type (file list, directory, saved file).
        """
        source = source or self.dirPath
        # extract list of files
        if type(source) is list:
            if len(source) <= 1:
                if os.path.isdir(source[0]):
                    files = self.extract_dir(source.pop())
            for file in source:
                if not os.path.isfile(file):
                    raise IOError("{path} is not a file.".format(path=file))
                    return
            files = set(map(os.path.abspath, source))
        elif os.path.isdir(source):
            files=self.extract_dir(source)
        else:
            files = set(source)
        return files

    def update(self, source=None):
        files = self.extract_source(source)

        # exclude already known files
        files = files.difference(set(self.files))

        # sort files before adding them
        try:
            files = sorted(files, key=self.validate_filepath)
        except (ValueError, IOError) as error:
            raise
            return

        # load files
        for file in files:
            self.add_step(file)

        return files

    def save(self, path):
        "Save method for titration object"
        try:
            # matplotlib objects can't be saved
            stackedHist = self.stackedHist
            hist = self.hist
            self.stackedHist= None
            self.hist = dict()
            with open(path, 'wb') as saveHandle:
                pickle.dump(self, saveHandle)
            # restore matplotlib objects
            self.stackedHist = stackedHist
            self.hist = hist
        except IOError as fileError:
            print("Could not save titration : {error}\n".format(error=fileError), file=sys.stderr)

    def load(self, path):
        "Loads previously saved titration in place of current instance"
        try:
            with open(path, 'rb') as loadHandle:
                self = pickle.load(loadHandle)
                if type(self) == Titration:
                    return self
                else:
                    raise ValueError("{file} does not contain a Titration object".format(file=path))
        except (ValueError, IOError) as loadError:
            print("Could not load titration : {error}\n".format(error=loadError), file=sys.stderr)

## -------------------------------------------
##      Properties
## -------------------------------------------
    @property
    def concentrationRatio(self):
    	return [value for value in self.protocole['[titrant]/[analyte]']]
    @property
    def summary(self):
        "Returns a short summary of current titration status as string."
        summary = '\n'.join(["--------------------------------------------",
                            "> {name}".format(name=self.name),
                            "--------------------------------------------",
                            "Source dir :\t{dir}".format(dir=self.dirPath),
                            "Steps :\t\t{steps} (reference step 0 to {last})".format(steps=self.dataSteps, last=max(self.dataSteps -1, 0)),
                            "Cut-off :\t{cutoff}".format(cutoff=self.cutoff),
                            "Total residues :\t\t{res}".format(res=len(self.residues)),
                            " - Complete residues :\t\t{complete}".format(complete=len(self.complete)),
                            " - Incomplete residues :\t{incomplete}".format(incomplete=len(self.incomplete)),
                            " - Filtered residues :\t\t{filtered}".format(filtered=len(self.filtered)),
                            "--------------------------------------------\n"  ])
        return summary


## ------------------------
##    Plotting
## ------------------------

    def plot_hist (self, step = None, show=True):
        """
        Define all the options needed (step, cutoof) for the representation.
        Call the getHistogram function to show corresponding histogram plots.
        """
        if not step: # plot stacked histograms of all steps
            # close stacked hist if needed
            if self.stackedHist and not self.stackedHist.closed:
                self.stackedHist.close()
            # replace stacked hist with new hist
            hist = MultiHist(self.complete,self.intensities[1:])
            self.stackedHist = hist
        else: # plot specific titration step
            # allow accession using python-ish negative index
            step = step if step >= 0 else self.dataSteps + step
            # close existing figure if needed
            if self.hist.get(step) and not self.hist[step].closed:
                self.hist[step].close()
            # plot new hist
            hist = Hist(self.complete, self.intensities[step], step=step)
            self.hist[step] = hist
        # add cutoff change event handling
        hist.add_cutoff_listener(self.set_cutoff, mouseUpdateOnly=True)
        if show:
            hist.show()
        hist.set_cutoff(self.cutoff)
        return hist


    def plot_shiftmap(self, residues, split = False):
        """
        Plot measured chemical shifts for each residue as a scatter plot of (chemshiftH, chemshiftN).
        Each color is assigned to a titration step.
        `residue` argument should be an iterable of AminoAcid objects.
        If using `split` option, each residue is plotted in its own subplot.
        """
        residues = list(residues)
        if split and len(residues) > 1:
            shiftmap = SplitShiftMap(residues)
        else: # Trace global chem shifts map
            shiftmap = ShiftMap(residues)
        shiftmap.show()
        return shiftmap


    def plot_titration(self, residue):
        "Plots a titration curve for `residue`, using intensity at each step"
        curve = TitrationCurve(self.concentrationRatio[:self.dataSteps], residue,
                                titrant=self.titrant['name'],
                                analyte=self.analyte['name'])
        curve.show()
        return curve


