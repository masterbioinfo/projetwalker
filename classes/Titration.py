#!/usr/bin/python3

"""
Titration class module

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
from math import *

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FormatStrFormatter

from classes.AminoAcid import AminoAcid
from classes.plots import Hist, MultiHist
from classes.widgets import CutOffCursor



class BaseTitration(object):

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
    def status(self):
        if not self.isInit:
            return None

        return "\n".join([  "------- Titration --------------------------",
                            " >\t{name}".format(name=self.name),
                            "------- Initial parameters -----------------",
                            "[{name}] :\t{concentration} µM".format(**self.titrant),
                            "[{name}] :\t{concentration} µM".format(**self.analyte),
                            "{name} volume  :\t{volume} µL".format(**self.analyte, volume=self.analyteStartVol),
                            "Initial volume :\t{volume} µL".format(volume=self.startVol),
                            "------- Current status ---------------------",
                            "Titration steps :\t\t{steps}".format(steps=list(range(self.steps))),
                            "{titrant} volumes (µL):\t{added}".format(
                                titrant=self.titrant['name'],added=self.volumes),
                            "Cumulated volumes (µL):\t{cumul}".format(cumul=self.volTitrant),
                            "Total volume (µL):\t{total}".format(total=self.volTotal),
                            "[{name}] (µM):\n\t\t{conc}".format(
                                name = self.titrant['name'], 
                                conc=[round(c, 4) for c in self.concentrationTitrant]),
                            "[{name}] (µM):\n\t\t{conc}".format(
                                name = self.analyte['name'], 
                                conc=[round(c, 4) for c in self.concentrationAnalyte]),
                            "[{titrant}]/[{analyte}] :".format(
                                titrant=self.titrant['name'], analyte=self.analyte['name']),
                            "\t\t{ratio}".format(ratio=[round(ratio,4) for ratio in self.concentrationRatio]) ])
                            
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
        return {
            'name' : self.name,
            'titrant' : self.titrant,
            'analyte' : self.analyte,
            'start_volume': {
                "analyte" : self.analyteStartVol,
                "total" : self.startVol
            },
            'add_volumes': self.volumes
        }

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
            initDict = {"_description" : "This file defines a titration's initial parameters."}
            fh = open(initFile, 'w', newline='') if initFile else sys.stdout
            initDict.update(self.as_init_dict)
            yaml.dump(initDict, fh, default_flow_style=False, indent=4)
            if fh is not sys.stdout:
                fh.close()
        except IOError as fileError:
            print("{error}".format(error=fileError), file=sys.stderr)
            return

    def csv(self, file=None):
        try:
            fh = open(file, 'w', newline='') if file else sys.stdout
            fieldnames = [  "#step",
                            "vol added {titrant} (µL)".format(titrant=self.titrant['name']),
                            "vol {titrant} (µL)".format(titrant=self.titrant['name']),
                            "vol total (µL)",
                            "[{analyte}] (µM)".format(analyte=self.analyte['name']),
                            "[{titrant}] (µM)".format(titrant=self.titrant['name']),
                            "[{titrant}]/[{analyte}]".format(titrant=self.titrant['name'], analyte=self.analyte['name'])    ]

            writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter='\t')

            writer.writeheader()
            for step in range(min(self.steps, len(self.volumes))):
                writer.writerow(self.step_as_dict(step))
            if fh is not sys.stdout:
                fh.close()
        except (IOError, IndexError) as error:
            print("{error}".format(error=error), file=sys.stderr)
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
    PATHPATTERN = re.compile(r'(.+/)?(.*[^\d]+)(?P<step>[0-9]+)\.list')
    # accepted lines pattern
    LINEPATTERN = re.compile(r'^(?P<position>\d+)(\S*)?\s+'
                        r'(?P<chemshiftH>\d+\.\d+)\s+'
                        r'(?P<chemshiftN>\d+\.\d+)$')
    # ignored lines pattern
    IGNORELINEPATTERN = re.compile(r"^\d.*")
    # source paths


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
        self.dirPath = None
        # init plots
        self.stackedHist = None
        self.hist = dict()
        #super().__init__()

        BaseTitration.__init__(self)

        ## FILE PATH PROCESSING
        # keep track of source path

        # fetch all .list files in source dir
        try:
            self.extract_source(source)
        except ValueError as error:
            print("{error}".format(error=error), file=sys.stderr)
            exit(1)
       
        # sort files by ascending titration number
        self.files.sort(key=self.validate_filepath)

        ## TITRATION PARAMETERS
        if self.dirPath and initFile is None:
            initFile = self.extract_init_file(self.dirPath)
        super().__init__(initFile)

        ## FILE PARSING
        for titrationFile in self.files:
            self.add_step(titrationFile)


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
        try:

            matching = self.PATHPATTERN.match(filePath) # attempt to match
            if matching:
                if verifyStep and int(matching.group("step")) != self.dataSteps:
                    raise IOError("File {file} expected to contain data for titration step #{step}.\
                 Are you sure this is the file you want ? \
                 In this case it must be named like *{step}.list".format(file=titrationFile, step=self.dataSteps))
                # retrieve titration step number parsed from file name
                return int(matching.group("step"))
            else:
                # found incorrect line format
                raise IOError("Refusing to parse file {file} : please check it is named like \{name\}\{step\}.list".format(file=filePath))
        except IOError as err:
            print("{error}".format(error=err), file=sys.stderr )
            exit(1)


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
                    self.parse_line(line)

        except IOError as fileError:
            print("{error}".format(error=error), file=sys.stderr)
            exit(1)
        except ValueError as parseError:
            print("{error} at line {line} in file {file}".format(
                error=parseError, line=lineNb, file=titrationFile), file=sys.stderr)

    def parse_line(self, line):
        line = line.strip()
        # ignore empty lines and header lines
        if self.IGNORELINEPATTERN.match(line):
            # attempt to match to expected format
            match = self.LINEPATTERN.match(line)
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


    def plot_shiftmap(self, residues=None, split = False):
        """
        Plot measured chemical shifts for each residue as a scatter plot of (chemshiftH, chemshiftN).
        Each color is assigned to a titration step.
        `residue` argument should be an iterable of AminoAcid objects.
        If using `split` option, each residue is plotted in its own subplot.
        """

        if residues:
            residueSet = [res for res in residues if res.position not in self.incomplete]
            if not residueSet: return
        elif split and self.filtered: # plot filtered residue by default when in split mode
            residueSet = self.filtered.values()
        else:
            split = False
            residueSet = self.complete.values() # using complete residues by default

        if len(residueSet) > 36 and split:
            raise ValueError("Refusing to plot so many ({count}) residues in split mode. Sorry.".format(count=len(residueSet)))

        fig = plt.figure()

        # set title
        fig.suptitle('Chemical shifts 2D map')
        # set common xlabel and ylabel
        fig.text(0.5, 0.04, 'H Chemical Shift', ha='center')
        fig.text(0.04, 0.5, 'N Chemical Shift', va='center', rotation='vertical')
        if split and len(residueSet) > 1:
            # create an array of cells with squared shape
            axes = fig.subplots(nrows=ceil(sqrt(len(residueSet))),
                                ncols=round(sqrt(len(residueSet))),
                                sharex=False, sharey=False, squeeze=True)
            # iterate over each created cell
            for index, ax in enumerate(axes.flat):
                if index < len(residueSet):
                    res = residueSet[index]
                    # Trace chem shifts for current residu in new graph cell
                    im = ax.scatter(res.chemshiftH, res.chemshiftN,
                                    facecolors='none', cmap=self.colors,
                                    c = range(self.dataSteps), alpha=0.2)
                    # ax.set_title("Residue %s " % res.position, fontsize=10)
                    # print xticks as 2 post-comma digits float
                    ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
                    ax.tick_params(labelsize=8)
                else:
                    ax.remove() # remove extra subplots

            # scale
            self.scale_split_shiftmap(residueSet, axes)
            # annotate
            for index, ax in enumerate(axes.flat):
                if index < len(residueSet):
                    self.annotate_chemshift(residueSet[index], ax)

            # display them nicely
            fig.tight_layout()
            # Add colorbar legend for titration steps using last plot cell data
            fig.subplots_adjust(left=0.12, top=0.9,
                                right=0.85,bottom=0.15) # make room for legend
            cbar_ax = fig.add_axes([0.90, 0.15, 0.02, 0.75])
            fig.colorbar(mappable=im, cax=cbar_ax).set_label("Titration steps")

        else: # Trace global chem shifts map
            for residue in residueSet :
                im=plt.scatter(residue.chemshiftH, residue.chemshiftN,
                                facecolors='none', cmap=self.colors,
                                c = range(self.dataSteps), alpha=0.2)
            fig.subplots_adjust(left=0.15, top=0.90,
                                right=0.85, bottom=0.15) # make room for legend
            # Add colorbar legend for titration steps
            cbar_ax = fig.add_axes([0.90, 0.15, 0.02, 0.75])
            fig.colorbar(mappable=im, cax=cbar_ax).set_label("Titration steps")

        fig.show()
        return fig


    def plot_titration(self, residue):
        xAxis = self.concentrationRatio
        yAxis = list(residue.chemshiftIntensity)
        fig = plt.figure()
        # set title
        fig.suptitle('Titration curve of residue {pos}'.format(pos=residue.position, fontsize=13))
        # set common xlabel and ylabel
        plt.xlabel("[{titrant}]/[{analyte}]".format(
            titrant=self.titrant['name'], analyte=self.analyte['name']))

        fig.text(0.04, 0.5, 'Chem Shift Intensity',
                va='center', rotation='vertical', fontsize=11)
        im = plt.scatter(xAxis, yAxis, alpha=1)
        """
        z = np.polyfit(xAxis, yAxis, 4)
        f = np.poly1d(z)

        xnew = np.linspace(0,max(xAxis),100)
        ynew = f(xnew)
        plt.plot(xnew, ynew)
        """
        """
        fig.subplots_adjust(left=0.12, top=0.90,
                            right=0.85,bottom=0.14) # make room for legend
        # Add colorbar legend for titration steps
        cbar_ax = fig.add_axes([0.90, 0.15, 0.02, 0.75])
        fig.colorbar(mappable=im, cax=cbar_ax).set_label("Titration steps")
        """
        fig.show()
        return fig


    def annotate_chemshift(self, residue, ax):
        "Adds chem shift vector and residue position for current residue in current subplot"
        xlim, ylim = ax.get_xlim(), ax.get_ylim()
        xrange, yrange = (xlim[1] - xlim[0], ylim[1] - ylim[0])

        shiftVector = np.array(residue.arrow[2:])
        orthoVector = np.array([1.0,1.0])
        # make orthogonal
        orthoVector -= orthoVector.dot(shiftVector) * shiftVector / np.linalg.norm(shiftVector)**2
        # scale ratio
        orthoVector *= np.array([xrange/yrange, 1.0])
        # normalize
        orthoVector /= (np.linalg.norm(orthoVector) * 10)

        """
        # plot using mpl arrow
        ax.arrow(*np.array(residue.arrow[:2]) + x, *residue.arrow[2:],
                head_width=0.07, head_length=0.1, fc='red', ec='red', lw=0.5,
                length_includes_head=True, linestyle='-', alpha=0.7, overhang=0.7)
        """
        arrowStart = np.array(residue.arrow[:2]) + orthoVector
        ax.annotate("", xy=arrowStart + shiftVector, xytext=arrowStart,
                    arrowprops=dict(arrowstyle="->", fc="red", ec='red', lw=0.5))
        """
        # show orthogonal vector
        ax.arrow(*residue.arrow[:2], *x, head_width=0.02, head_length=0.02, fc='black', ec='green',
                length_includes_head=True, linestyle=':', alpha=0.6, overhang=0.5)
        """
        horAlign = "left" if orthoVector[0] <=0 else "right"
        vertAlign = "top" if orthoVector[1] >=0 else "bottom"
        ax.annotate(str(residue.position), xy=residue.chemshift[0],
                    xytext=residue.chemshift[0]-0.8*orthoVector,
                    xycoords='data', textcoords='data',
                    fontsize=7, ha=horAlign, va=vertAlign)


    def scale_split_shiftmap(self, residueSet, axes):
        "Scales subplots when plotting splitted shift map"
        xMaxRange, yMaxRange = np.array(self.get_max_range_NH(residueSet)) * 1.5
        for ax in axes.flat:
            currentXRange = ax.get_xlim()
            currentYRange = ax.get_ylim()
            xMiddle = sum(currentXRange) / 2
            yMiddle = sum(currentYRange) / 2
            ax.set_xlim(xMiddle - xMaxRange/2, xMiddle + xMaxRange/2)
            ax.set_ylim(yMiddle - yMaxRange/2, yMiddle + yMaxRange/2)


## -------------------------
##    Utils
## -------------------------

    def extract_source(self, source):
        """
        Handles source data depending on type (file list, directory, saved file).
        Should be called only on __init__()
        """
        if type(source) is list: # or use provided source as files
            self.files = source
            self.dirPath = os.path.dirname(source[0])
        elif os.path.isdir(source):
            self.dirPath = os.path.abspath(source)
            self.files = [ os.path.join(self.dirPath, titrationFile) for titrationFile in os.listdir(self.dirPath) if titrationFile.endswith(".list") ]
            if len(self.files) < 1:
                raise ValueError("Directory {dir} does not contain any `.list` titration file.".format(dir=self.dirPath))
        elif os.path.isfile(source):
            return self.load(source)
        self.source = source
        return self.files

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

    def get_max_range_NH(self, residueSet):
        "Returns max range tuple for N and H among residues in residueSet"
        return (max([res.rangeH for res in residueSet]),
                max([res.rangeN for res in residueSet]))

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
            return dict([(res.position,res) for res in self.complete.values() if res.chemshiftIntensity[-1] >= self.cutoff])
        else:
            return []

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