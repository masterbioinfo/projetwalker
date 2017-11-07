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

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

import numpy as num
from math import *
import os, re, sys
import pickle

from classes.AminoAcid import AminoAcid
from classes.widgets import CutOffCursor
from classes.plots import Hist, MultiHist

class TitrationStep(object):
	steps = 0

	def __init__(self, titration, volumeAdded):
		self.id = type(self).steps
		type(self).steps += 1

	def __del__(self):
		type(self).steps -= 1



class Titration(object):
	"""
	Class Titration.
	Contains a list of aminoacid objects
	Provides methods for accessing each titration step datas.
	"""
	# accepted file path pattern
	rePath = re.compile(r'(.+/)?(.*[^\d]+)(?P<step>[0-9]+)\.list')
	# accepted lines pattern
	reLine = re.compile(r"^(?P<position>\d+)(\S*)?\s+(?P<chemShiftH>\d+\.\d+)\s+(?P<chemShiftN>\d+\.\d+)$")
	# ignored lines pattern
	reLineIgnore = re.compile(r"^\d.*")
	# source paths
	

	def __init__(self, source, name=None, cutOff = None):
		"""
		Load titration files, check their integrity
		`source` is either a directory containing `.list` file, or is a list of `.list` files
		Separate complete vs incomplete data
		"""

		# Placeholder for naming saved titrations
		self.name = name or "Unnamed Titration"
		self.residues = dict() # all residues {position:AminoAcid object}
		self.complete = dict() # complete data residues
		self.incomplete = dict() # incomplete data res
		self.selected = dict()
		self.intensities = list() # 2D array of intensities
		self.steps = 0 # titration steps counter
		self.cutOff = None
		self.source = None
		self.dirPath = None
		# init plots
		self.stackedHist = None
		self.hist = dict()

		## FILE PATH PROCESSING
		# keep track of source path
		self.source = source
		# fetch all .list files in source dir
		try:
			if type(source) is list: # or use provided source as files
				self.files = source
				self.dirPath = os.path.dirname(source[0])
			elif os.path.isdir(source):
				self.files = [ os.path.join(self.source, titrationFile) for titrationFile in os.listdir(source) if ".list" in titrationFile ]
				self.dirPath = os.path.abspath(source)
				if len(self.files) < 1:
					raise ValueError("Directory %s does not contain any `.list` titration file." % self.dirPath)
			elif os.path.isfile(source):
				return self.load(source)
		except ValueError as error:
			print("%s" % error, file=sys.stderr)
			exit(1)
		
		# sort files by ascending titration number
		self.files.sort(key=lambda path: self.validate_filepath(path))

		## FILE PARSING
		for titrationFile in self.files:
			self.add_step(titrationFile)
		
		## INIT CUTOFF
		if cutOff:
			self.set_cutoff(cutOff)

		self.protLigRatio = list()

	def add_step(self, titrationFile):
		"Adds a titration step described in `titrationFile`"
		print("[Step %s]\tLoading file %s" % (self.steps, titrationFile), file=sys.stderr)
		# verify file
		step = self.validate_filepath(titrationFile, verifyStep=True)
		# parse it
		self.parse_titration_file(titrationFile)
		self.steps += 1 # increase number of titration steps
		# filter complete residues as list and sort them by positions
		for pos in range(min(self.residues), max(self.residues)):
			if pos not in self.residues:
				self.residues[pos] = AminoAcid(position=pos)
		self.complete = dict()
		for pos, res in self.residues.items():
			if res.validate(self.steps):
				self.complete[pos] = res
			else:
				self.incomplete[pos] = res
				
		print("\t\t%s incomplete residue out of %s" % (
			 len(self.incomplete), len(self.complete)), file=sys.stderr)

		# Recalculate (position, chem shift intensity) coordinates for histogram plot
		self.intensities = [] # 2D array, by titration step then residu position
		for step in range(self.steps - 1): # intensity is null for reference step, ignoring
			self.intensities.append([residue.chemShiftIntensity[step] for residue in self.complete.values()])
		# generate colors for each titration step
		self.colors = plt.cm.get_cmap('hsv', self.steps)
		# close stale stacked hist
		if self.stackedHist and not self.stackedHist.closed:
			self.stackedHist.close()




	def set_name(self, name):
		"Sets Titration instance name"
		self.name = str(name)
		return self.name

	def select_residues(self, *positions):
		"Select a subset of residues"
		for pos in positions:
			try:
				self.selected[pos] = self.residues[pos]
			except KeyError:
				print("Residue at position %s does not exist. Skipping selection." % pos, file=sys.stderr)
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

	def set_cutoff(self, cutOff):
		"Sets cut off for all titration steps"
		try:
			# check cut off validity and store it
			cutOff = float(cutOff)
			self.cutOff = cutOff
			# update cutoff in open hists
			for hist in self.hist.values():
				hist.set_cutoff(cutOff)
			if self.stackedHist:
				self.stackedHist.set_cutoff(cutOff)
			#sys.stdout.write("\r\nCut-off=%s\r\n>> " % cutOff)
			return self.cutOff
		except TypeError as err:
			sys.stderr.write("Invalid cut-off value : %s\n" % err)
			return self.cutOff




	def validate_filepath(self, filePath, verifyStep=False):
		"""
		Given a file path, checks if it has .list extension and if it is numbered after the titration step.
		If `step` arg is provided, validation will enforce that parsed file number matches `step`.
		Returns the titration step number if found, IOError is raised otherwise
		"""
		try:
			
			matching = self.rePath.match(filePath) # attempt to match
			if matching:
				if verifyStep and int(matching.group("step")) != self.steps:
					raise IOError("File %s expected to contain data for titration step #%s.\
				 Are you sure this is the file you want ? \
				 In this case it must be named like *[0-9]+.list" % (titrationFile, self.steps))
				# retrieve titration step number parsed from file name
				return int(matching.group("step"))
			else:
				# found incorrect line format
				raise IOError("Refusing to parse file %s : please check it is named like *[0-9]+.list" % filePath)
		except IOError as err:
			sys.stderr.write("%s\n" % err )
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
					line = line.strip()
					# ignore empty lines and header lines
					if self.reLineIgnore.match(line):
						# attempt to match to expected format
						lineMatch = self.reLine.match(line)
						if lineMatch: # parse as dict
							chemShift = lineMatch.groupdict()
							# Convert parsed str to number types 
							for castFunc, key in zip((float, float, int), sorted(chemShift)):
								chemShift[key] = castFunc(chemShift[key])
							# add or update residue
							position = chemShift["position"]
							if self.residues.get(position):
								# update AminoAcid object in residues dict
								self.residues[position].add_chemshift(**chemShift)
							else:
								# create AminoAcid object in residues dict
								self.residues[position] = AminoAcid(**chemShift)
						else:
							# non parsable, non ignorable line
							raise ValueError("Could not parse file %s at line %s" % (titrationFile, lineNb))

		except (IOError, ValueError) as error:
			sys.stderr.write("%s\n" % error)
			exit(1)


	def plot_hist (self, step = None, showCutOff = True,
								scale=True, show=True):
		"""
		Define all the options needed (step, cutoof) for the representation.
		Call the getHistogram function to show corresponding histogram plots.
		"""
		if not step: # plot stacked histograms of all steps
			# close stacked hist if needed
			if self.stackedHist and not self.stackedHist.closed:
				self.stackedHist.close()
			# replace stacked hist with new hist
			hist = MultiHist(self.complete,self.intensities)
			self.stackedHist = hist
		else: # plot specific titration step
			# allow accession using python-ish negative index
			step = step if step >= 0 else self.steps + step
			# close existing figure if needed
			if self.hist.get(step) and not self.hist[step].closed:
				self.hist[step].close()
			# plot new hist
			hist = Hist(self.complete, self.intensities[step-1], step=step)
			self.hist[step] = hist
		# add cutoff change event handling
		hist.add_cutoff_listener(self.set_cutoff, mouseUpdateOnly=True)
		if show:
			hist.show()
		if showCutOff and self.cutOff:
			hist.set_cutoff(self.cutOff)
		return hist

	def plot_shiftmap(self, residues=None, split = False):
		"""
		Plot measured chemical shifts for each residue as a scatter plot of (chemShiftH, chemShiftN).
		Each color is assigned to a titration step.
		`residue` argument should be an iterable of AminoAcid objects.
		If using `split` option, each residue is plotted in its own subplot.
		"""
		
		if residues:
			residueSet = [res for res in residues if res.position not in self.incomplete]
			if not residueSet: return
		elif split and self.filtered:
			residueSet = self.filtered.values()
		else:
			split = False
			residueSet = self.complete.values() # using complete residues by default
		
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
					im = ax.scatter(res.chemShiftH, res.chemShiftN,
									facecolors='none', cmap=self.colors, 
									c = range(self.steps), alpha=0.2)
					# ax.set_title("Residue %s " % res.position, fontsize=10)
					# print xticks as 2 post-comma digits float
					ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
					ax.tick_params(labelsize=8)
				else:
					ax.remove() # remove extra subplots

			# scale
			self.scale_split_shiftmap(residueSet, axes)
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
				im=plt.scatter(residue.chemShiftH, residue.chemShiftN, 
								facecolors='none', cmap=self.colors, 
								c = range(self.steps), alpha=0.2)
			fig.subplots_adjust(left=0.15, top=0.90,
								right=0.85,bottom=0.15) # make room for legend
			# Add colorbar legend for titration steps
			cbar_ax = fig.add_axes([0.90, 0.15, 0.02, 0.75])
			fig.colorbar(mappable=im, cax=cbar_ax).set_label("Titration steps")

		fig.show()
		return fig


	def plot_titration(self, residue):
		
		if self.protLigRatio is not None:
			intensitiesPerResidu = self.complete[int(residue)].chemShiftIntensity
			steps = [ step for step in range(1,self.steps) ]
			
			fig = plt.figure()
			# set title
			fig.suptitle('Titration Curve of residue ' + str(residue), fontsize=13)
			# set common xlabel and ylabel
			fig.text(0.5, 0.04, 'Ligand-to-Protein Concentration Ratio', ha='center', fontsize=11)
			fig.text(0.04, 0.5, 'Intensity (ppm)', 
					va='center', rotation='vertical', fontsize=11)
			im=plt.scatter(self.protLigRatio, intensitiesPerResidu, 
							facecolors='none', cmap=self.colors, 
							c = steps, alpha=0.2)
			fig.subplots_adjust(left=0.12, top=0.90,
								right=0.85,bottom=0.14) # make room for legend
			# Add colorbar legend for titration steps
			cbar_ax = fig.add_axes([0.90, 0.15, 0.02, 0.75])
			fig.colorbar(mappable=im, cax=cbar_ax).set_label("Titration steps")

			fig.show()
			return fig

		else:
			print("No Ligand-to-Protein concentration ratio found.")

	def protLigCalcul(self, protInitConc, ligInitConc, totVol, protVol, ligVol, overwrite = False):
		if overwrite:
			self.protLigRatio = list()
		for index in range(0,len(protVol)):
			protFinalConc = protInitConc*protVol[index]/totVol[index]
			ligFinalConc = ligInitConc*(ligVol)/totVol[index]
			self.protLigRatio.append(protFinalConc/ligFinalConc)
		if len(self.protLigRatio) == self.steps:
			del(self.protLigRatio[0])
		print(" ".join(map(str,self.protLigRatio)))
		return self.protLigRatio

	def annotate_chemshift(self, residue, ax):
		"Adds chem shift vector and residue position for current residue in current subplot"
		xlim, ylim = ax.get_xlim(), ax.get_ylim()
		xrange, yrange = (xlim[1] - xlim[0], ylim[1] - ylim[0])
		
		shiftVector = num.array(residue.arrow[2:])
		orthoVector = num.array([1.0,1.0])
		# make orthogonal
		orthoVector -= orthoVector.dot(shiftVector) * shiftVector / num.linalg.norm(shiftVector)**2
		# scale ratio
		orthoVector *= num.array([xrange/yrange, 1.0])
		# normalize
		orthoVector /= (num.linalg.norm(orthoVector) * 10)
		
		"""
		# plot using mpl arrow
		ax.arrow(*num.array(residue.arrow[:2]) + x, *residue.arrow[2:],
				head_width=0.07, head_length=0.1, fc='red', ec='red', lw=0.5,
				length_includes_head=True, linestyle='-', alpha=0.7, overhang=0.7)
		"""
		arrowStart = num.array(residue.arrow[:2]) + orthoVector
		ax.annotate("", xy=arrowStart + shiftVector, xytext=arrowStart,
    				arrowprops=dict(arrowstyle="->", fc="red", ec='red', lw=0.5))
		"""
		# show orthogonal vector
		ax.arrow(*residue.arrow[:2], *x, head_width=0.02, head_length=0.02, fc='black', ec='green', 
				length_includes_head=True, linestyle=':', alpha=0.6, overhang=0.5)
		"""
		horAlign = "left" if x[0] <=0 else "right"
		vertAlign = "top" if x[1] >=0 else "bottom"
		ax.annotate(str(residue.position), xy=residue.chemShift[0], 
					xytext=residue.chemShift[0]-0.8*orthoVector,
					xycoords='data', textcoords='data', 
					fontsize=7, ha=horAlign, va=vertAlign)

	def get_max_range_NH(self, residueSet):
		"Returns max range tuple for N and H among residues in residueSet"
		return (max([res.rangeH for res in residueSet]),
				max([res.rangeN for res in residueSet]))

	def scale_split_shiftmap(self, residueSet, axes):
		"Scales subplots when plotting splitted shift map"
		xMaxRange, yMaxRange = num.array(self.get_max_range_NH(residueSet)) * 1.5
		for ax in axes.flat:
			currentXRange = ax.get_xlim()
			currentYRange = ax.get_ylim()
			xMiddle = sum(currentXRange) / 2
			yMiddle = sum(currentYRange) / 2
			ax.set_xlim(xMiddle - xMaxRange/2, xMiddle + xMaxRange/2)
			ax.set_ylim(yMiddle - yMaxRange/2, yMiddle + yMaxRange/2)

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
			sys.stderr.write("Could not save titration : %s\n" % fileError)

	def load(self, path):
		"Loads previously saved titration in place of current instance"
		try:
			with open(path, 'rb') as loadHandle:
				self = pickle.load(loadHandle)
				if type(self) == Titration:
					return self
				else:
					raise ValueError("%s does not contain a Titration object" % path)
		except (ValueError, IOError) as loadError:
			sys.stderr.write("Could not load titration : %s\n" % loadError)


##--------------------------
##	Properties
##--------------------------

	@property
	def filtered(self):
		"Returns list of filtered residue having last intensity >= cutoff value"
		if self.cutOff is not None:
			return  dict([(res.position,res) for res in self.complete.values() if res.chemShiftIntensity[self.steps-2] >= self.cutOff])
		else:
			return []

	@property
	def sortedSteps(self):
		"""
		Sorted list of titration steps, beginning at step 1.
		Reference step 0 is ignored.
		"""
		return sorted(range(1,self.steps))

	@property
	def summary(self):
		"Returns a short summary of current titration status as string."
		summary =   "--------------------------------------------\n"
		summary += "> %s\n" % self.name
		summary +=  "--------------------------------------------\n"
		summary += "Source dir :\t%s\n" % self.dirPath
		summary += "Steps :\t\t%s (reference step 0 to %s)\n" % (self.steps, self.steps -1)
		summary += "Cut-off :\t%s\n" % self.cutOff
		summary += "Total residues :\t\t%s\n" % len(self.residues)
		summary += " - Complete residues :\t\t%s\n" % len(self.complete)
		summary += " - Incomplete residues :\t%s\n" % len(self.incomplete)
		summary += " - Filtered residues :\t\t%s\n" % len(self.filtered)
		summary +=  "--------------------------------------------\n"
		return summary