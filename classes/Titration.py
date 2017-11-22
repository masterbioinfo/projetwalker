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
from astropy.table import Table, Column, MaskedColumn

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FormatStrFormatter

from classes.AminoAcid import AminoAcid
from classes.plots import Hist, MultiHist, ShiftMap, SplitShiftMap, TitrationCurve
from classes.widgets import CutOffCursor



represent_dict_order = lambda self, data:  self.represent_mapping('tag:yaml.org,2002:map', data.items())
""" setup YAML for ordered dict output : https://stackoverflow.com/a/8661021 """
yaml.add_representer(OrderedDict, represent_dict_order)


class BaseTitration(object):

    INIT_FIELDS=('name', 'analyte', 'titrant', 'start_volume', 'add_volumes')

    def __init__(self, initFile=None):
        self.isInit = False
        self.initFile = None
        self.name = "Unnamed Titration"
        self.analyte = {
            "name" : "analyte",
            "concentration" : 0
        }
        self.titrant = {
            "name" : "titrant",
            "concentration" : 0
        }
        self.startVol = 0
        self.analyteStartVol = 0

        self.steps = 0

        self.volumes = list()
        if initFile is not None:
            self.load_init_file(initFile)

        self.FIELDS = {
            'steps': {'description': 'Step'},
            'vol_add': {
                'description': '{titrant} vol added'.format(titrant=self.titrant['name']),
                'unit': 'µL'
            },
            'vol_cumul': {
                'description': 'Total {titrant} vol'.format(titrant=self.titrant['name']),
                'unit': 'µL'
            },
            'vol_tot': {
                'description': 'Total vol',
                'unit': 'µL'
            },
            'conc_titrant': {
                'description': '[{titrant}]'.format(titrant=self.titrant['name']),
                'unit': 'µM'
            },
            'conc_analyte': {
                'description':'[{analyte}]'.format(analyte=self.analyte['name']),
                'unit': 'µM'
            },
            'conc_ratio': {
                'description': '[{titrant}]/[{analyte}]'.format(
                    titrant=self.titrant['name'], analyte=self.analyte['name']),
                'unit': 'µM'
            }
        }


## -------------------------------------------------
##         Manipulation methods
## -------------------------------------------------
    def set_name(self, name):
        "Sets Titration instance name"
        self.name = str(name)
        return self.name

    def add_step(self, volume = None):
        self.steps += 1
        if volume is not None: self.volumes.append(volume)
        return self.steps

    def set_volumes(self, volumes):
        self.steps = len(volumes)
        self.volumes = list(map(float, volumes))

    def update_volumes(self, stepVolumes):
        try:
            for step, vol in stepVolumes.items():
                self.volumes[step] = vol
        except IndexError:
            print("{step} does not exist")

    def add_volumes(self, volumes):
        for vol in volumes:
            self.add_step(vol)
        return self.steps

    def step_as_dict(self, step):
        dictStep = dict()
        dictStep["#step"] = step
        dictStep["vol added {titrant} (µL)".format(titrant=self.titrant['name']) ] = self.volumes[step]
        dictStep["vol {titrant} (µL)".format(titrant=self.titrant['name']) ] = self.volTitrant[step]
        dictStep["vol total (µL)"] = self.volTotal[step]
        dictStep["[{analyte}] (µM)".format(analyte=self.analyte['name']) ] = round(self.concentrationAnalyte[step], 4)
        dictStep["[{titrant}] (µM)".format(titrant=self.titrant['name']) ] = round(self.concentrationTitrant[step], 4)
        dictStep["[{titrant}]/[{analyte}]".format(titrant=self.titrant['name'], analyte=self.analyte['name']) ] = round(self.concentrationRatio[step], 4)
        return dictStep

## -----------------------------------------------------
##         Properties
## -----------------------------------------------------

    @property
    def protocole(self):
        order = ('steps', 'vol_add', 'vol_cumul', 'vol_tot', 'conc_titrant', 'conc_analyte', 'conc_ratio')
        protocole={
            'steps' : list(range(self.steps)),
            'vol_add': self.volumes,
            'vol_cumul' : self.volTitrant,
            'vol_tot': self.volTotal,
            'conc_titrant':[round(c, 4) for c in self.concentrationTitrant],
            'conc_analyte': [round(c, 4) for c in self.concentrationAnalyte],
            'conc_ratio' : [round(ratio,4) for ratio in self.concentrationRatio],
        }
        return OrderedDict([ (field, protocole[field]) for field in order ])

    @property
    def is_consistent(self):
        return True if len(self.volumes) == self.steps else False

    @property
    def volTitrant(self):
        volCumul = [0]
        for vol in self.volumes[1:]:
            volCumul.append(volCumul[-1] + vol)
        return volCumul

    @property
    def volTotal(self):
        return [vol + self.startVol for vol in self.volTitrant]

    @property
    def concentrationAnalyte(self):
        return [self.analyteStartVol*self.analyte['concentration'] / volTot for volTot in self.volTotal]

    @property
    def concentrationTitrant(self):
        return [volTitrantStep*self.titrant['concentration'] / volTot for volTitrantStep, volTot in zip(self.volTitrant, self.volTotal)]

    @property
    def concentrationRatio(self):
        return [concTitrant/concAnalyte for concTitrant, concAnalyte in zip(self.concentrationTitrant, self.concentrationAnalyte)]

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


    @property
    def protocole_as_table(self):
        table = Table()
        protocole = self.protocole
        for key, value in protocole.items():
            field = self.FIELDS[key]
            name = field['description']
            if field.get('unit'):
                name = "{name} ({unit})".format(name=name, unit=field['unit'])
            col = Column(value, **field, name=name)
            table.add_column(col)
        return table

## -----------------------------------------------------
##         Input/output
## -----------------------------------------------------
    def extract_init_file(self, dirPath):
        initFileList = glob.glob(os.path.join(dirPath, '*.yml')) or glob.glob(os.path.join(dirPath,'*.json'))
        if len(initFileList) > 1:
            initFile = min(initFileList, key=os.path.getctime)
            raise ValueError("{number} init files found in {source}. Using most recent one : {file}".format(
                                number=len(initFileList), source=dirPath, file=self.initFile ))
        elif initFileList:
            initFile = initFileList.pop()
        return initFile

    def check_init_file(self, initFile):
        try:
            root, ext = os.path.splitext(initFile)
            if ext == '.yml':
                    loader = yaml
            elif ext == '.json':
                    loader = json
            else:
                raise IOError("Invalid init file extension for {init} : accepted are .yml or .json".format(init=initFile))
            with open(initFile, 'r') as initHandle:
                initDict = loader.load(initHandle)
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
            print("Could not convert value to number : %s" % typeError)
            return None
        except IOError as fileError:
            print("{error}".format(error=fileError), file=sys.stderr)
            return None
        except KeyError as parseError:
            print("Missing required data in init file. Please check it is accurately formatted as JSON.")
            print("Hint: {error}".format(error=parseError), file=sys.stderr)
            return None
        except (ValueError,YAMLError) as valError:
            print("Error : {error}".format(error=valError), file=sys.stderr)
            return None

    def load_init_file(self, initFile):
        print("[Init]\t\tLoading titration protocole from {init}".format(init=initFile))
        initDict = self.check_init_file(initFile)
        if initDict is None:
            return
        self.titrant = initDict['titrant']
        self.analyte = initDict['analyte']
        self.name = initDict.get('name') or self.name
        self.analyteStartVol = float(initDict['start_volume']['analyte'])
        self.startVol = initDict['start_volume']['total']
        if initDict.get('add_volumes'):
            self.set_volumes(initDict['add_volumes'])
        self.initFile=initFile
        self.isInit = True
        return self.isInit

    def dump_init_file(self, initFile=None):
        try:

            fh = open(initFile, 'w', newline='') if initFile else sys.stdout
            yaml.dump(self.as_init_dict, fh, default_flow_style=False, indent=4)
            if fh is not sys.stdout:
                fh.close()
        except IOError as fileError:
            print("{error}".format(error=fileError), file=sys.stderr)
            return




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


    def __init__(self, source, name=None, cutoff = None, initFile=None, **kwargs):
        """
        Load titration files, check their integrity
        `source` is either a directory containing `.list` file, or is a list of `.list` files
        Separate complete vs incomplete data
        """

        self.name = ""
        self.residues = dict() # all residues {position:AminoAcid object}
        self.complete = dict() # complete data residues
        self.incomplete = dict() # incomplete data res
        self.selected = dict()
        self.intensities = list() # 2D array of intensities
        self.dataSteps = 0
        self.cutoff = None
        self.source = None
        self.files = []
        self.dirPath = None
        # init plots
        self.stackedHist = None
        self.hist = dict()

        BaseTitration.__init__(self)

        ## FILE PATH PROCESSING
        # fetch all .list files in source dir, parse
        # add a step for each file
        try:
            self.files = self.update(source)
        except IOError as error:
            print("{error}".format(error=error), file=sys.stderr)
            exit(1)


        ## TITRATION PARAMETERS
        if self.dirPath and initFile is None:
            initFile = self.extract_init_file(self.dirPath)
        super().__init__(initFile)


        ## INIT CUTOFF
        if cutoff:
            self.set_cutoff(cutoff)

        ## finish
        if not self.name:
            self.name = "Unnamed Titration"


## --------------------------------
##    Titration + RMN Analysis
## --------------------------------


    def add_step(self, titrationFile, volume=None):
        "Adds a titration step described in `titrationFile`"

        print("[Step {step}]\tLoading NMR data from {titration_file}".format(step=self.dataSteps, titration_file=titrationFile), file=sys.stderr)
        # verify file
        step = self.validate_filepath(titrationFile, verifyStep=True)
        # parse it
        self.parse_titration_file(titrationFile)
        self.dataSteps += 1
        if volume is not None:
            super().update_volumes({step:volume})
        if self.dataSteps < self.dataSteps:
            super().add_step(volume=volume)

        # create data-empty residues for missing positions
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
             incomplete=len(self.incomplete), total=len(self.complete)), file=sys.stderr)

        # Recalculate (position, chem shift intensity) coordinates for histogram plot
        self.intensities = [] # 2D array, by titration step then residu position
        for step in range(self.dataSteps): # intensity is null for reference step, ignoring
            self.intensities.append([residue.chemshiftIntensity[step] for residue in self.complete.values()])
        # generate colors for each titration step
        self.colors = plt.cm.get_cmap('hsv', self.dataSteps)
        # close stale stacked hist
        if self.stackedHist and not self.stackedHist.closed:
            self.stackedHist.close()

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
            print("Invalid cut-off value : {error}".format(error=err), file=sys.stderr)
            return self.cutoff

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
                                "In this case it must be named like *{step}.list".format(file=filePath, step=self.dataSteps))
            # retrieve titration step number parsed from file name
            return int(matching.group("step"))
        else:
            # found incorrect line format
            raise IOError("Refusing to parse file {file}.\nPlease check it is named like (name)(step).list".format(file=filePath))



    def parse_titration_file(self, titrationFile):
        """
        Titration file parser.
        Returns a new dict which keys are residues' position and values are AminoAcid objects.
        If residues argument is provided, updates AminoAcid by adding parsed chemical shift values.
        Throws ValueError if incorrect lines are encountered in file.
        """
        try :
            with open(titrationFile, "r", encoding = "utf-8") as titration:
                for lineNb, line in enumerate(titration) :
                    try:
                        self.parse_line(line)
                    except ValueError as parseError:
                        print("{error} at line {line} in file {file}".format(
                            error=parseError, line=lineNb, file=titrationFile), file=sys.stderr)
                        continue
        except IOError as fileError:
            print("{error}".format(error=error), file=sys.stderr)
            return

    def parse_line(self, line):
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
                return self.add_chemshifts(chemshifts)
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
        curve = TitrationCurve(self.concentrationRatio, residue,
                                titrant=self.titrant['name'],
                                analyte=self.analyte['name'])
        curve.show()
        return curve


## -------------------------
##    Utils
## -------------------------

    def extract_source(self, source):
        """
        Handles source data depending on type (file list, directory, saved file).
        Should be called only on __init__()
        """
        files = []
        if type(source) is list: # or use provided source as files
            for file in source:
                if not os.path.isfile(file):
                    raise IOError("{path} is not a file.".format(path=file))
                    return
            files = source
            self.dirPath = os.path.dirname(files[0])
        elif os.path.isdir(source):
            self.dirPath = os.path.abspath(source)
            files = glob.glob(os.path.join(self.dirPath, '*.list'))
            if len(files) < 1:
                raise ValueError("Directory {dir} does not contain any `.list` titration file.".format(dir=self.dirPath))
        elif os.path.isfile(source):
            return self.load(source)
        self.source = source
        return files

    def update(self, source=None):
        files = []
        if not source:
            if self.dirPath:
                files = self.extract_source(self.dirPath)
            else:
                raise IOError("Nothing to update from, please provide an argument (files or directory path)")
                return
        else:
            files = self.extract_source(source)
        # exclude already known file
        files = [ file for file in files if file not in self.files ]
        try:
            files = sorted(files, key=self.validate_filepath)
        except (ValueError, IOError) as error:
            raise error
            return
        for file in files:
            self.add_step(file)
        return files


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
            self.hist= hist
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
        return sorted(range(1,self.dataSteps))

    @property
    def summary(self):
        "Returns a short summary of current titration status as string."
        summary = '\n'.join(["--------------------------------------------",
                            "> {name}".format(name=self.name),
                            "--------------------------------------------",
                            "Source dir :\t{dir}".format(dir=self.dirPath),
                            "Steps :\t\t{steps} (reference step 0 to {last})".format(steps=self.dataSteps, last=self.dataSteps -1),
                            "Cut-off :\t{cutoff}".format(cutoff=self.cutoff),
                            "Total residues :\t\t{res}".format(res=len(self.residues)),
                            " - Complete residues :\t\t{complete}".format(complete=len(self.complete)),
                            " - Incomplete residues :\t{incomplete}".format(incomplete=len(self.incomplete)),
                            " - Filtered residues :\t\t{filtered}".format(filtered=len(self.filtered)),
                            "--------------------------------------------\n"  ])
        return summary

    @property
    def added(self):
        return self.volumes[:self.dataSteps] if len(volumes) >= self.dataSteps else self.volumes

    @property
    def pending(self):
        return self.volumes[self.dataSteps:] if self.dataSteps < len(volumes) else []
