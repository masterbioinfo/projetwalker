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

class Titration(object):
	"""
	Class Titration.
	Contains a list of aminoacid objects
	Provides methods for accessing each titration step datas.
	"""
	complete = list()
	incomplete = set()

	def __init__(self, source, name=None, cutOff = None):
		"""
		Load titration files, check their integrity
		`source` is either a directory containing `.list` file, or is a list of `.list` files
		Separate complete vs incomplete data
		"""

		# Placeholder for naming saved titrations
		self.name = name or "Unnamed Titration"
		# number of titration steps
		self.steps  = 0

		## FILE PATH PROCESSING
		# keep track of source data
		self.source = source
		# fetch all .list files in source dir
		if type(source) is list: # or use provided source as files
			self.files = source
			self.dirPath = os.path.dirname(source[0])
		elif os.path.isdir(source):
			self.files = [ os.path.join(self.source, titrationFile) for titrationFile in os.listdir(source) if ".list" in titrationFile ]
			self.dirPath = os.path.abspath(source)
		elif os.path.isfile(source):
			return self.load(source)
		# sort files by ascending titration number
		self.files.sort(key=lambda path: self.validateFilePath(path))

		## PLOTTING
		self.stackedHist = None
		self.hist = dict()
		self.positionTicks = None

		## FILE PARSING
		# init residues {position:AminoAcid object}
		self.residues = dict()
		# and fill it by parsing files
		for titrationFile in self.files:
			self.add_step(titrationFile)
		
		## INIT CUTOFF
		self.cutOff = None
		if cutOff:
			self.setCutOff(cutOff)

	def add_step(self, titrationFile):
		"Adds a titration step described in `titrationFile`"
		print("[Step %s]\tLoading file %s" % (self.steps, titrationFile), file=sys.stderr)
		# verify file
		step = self.validateFilePath(titrationFile, verifyStep=True)
		# parse it
		self.parseTitrationFile(titrationFile)
		self.steps += 1 # increase number of titration steps
		# filter complete residues as list and sort them by positions
		self.complete = sorted([ residue for residue in self.residues.values() if residue.validate(self.steps) ], key=lambda a: a.position)
		# incomplete residues
		self.incomplete = set(self.residues.values()) - set(self.complete)
		print("\t\t%s incomplete residue out of %s" % (
			 len(self.incomplete), len(self.complete)), file=sys.stderr)

		# Recalculate (position, chem shift intensity) coordinates for histogram plot
		self.intensities = [] # 2D array, by titration step then residu position
		self.positions = []
		for step in range(self.steps - 1): # intensity is null for reference step
			self.intensities.append( [ residue.chemShiftIntensity[step] for residue in self.complete ] )
		for residue in self.complete:
			self.positions.append(residue.position)

		# Update graph settings according to step change
		self.positionTicks = range(self.positions[0] - self.positions[0] % 5, self.positions[-1] + 10, 10)
		# generate colors for each titration step
		self.colors = plt.cm.get_cmap('hsv', self.steps)

		if self.stackedHist and not self.stackedHist.closed:
			self.stackedHist.close()


	@property
	def filtered(self):
		"Returns list of filtered residue having last intensity >= cutoff value"
		if self.cutOff:
			return  [residue for residue in self.complete if residue.chemShiftIntensity[self.steps-2] >= self.cutOff]
		else:
			return self.complete

	def setCutOff(self, cutOff):
		"Sets cut off for all titration steps"
		try:
			# check cut off validity and store it
			cutOff = float(cutOff)
			self.cutOff = cutOff
			# update cutoff in open hists
			for hist in self.hist.values():
				hist.setCutOff(cutOff)
			if self.stackedHist:
				self.stackedHist.setCutOff(cutOff)
			#sys.stdout.write("\r\nCut-off=%s\r\n>> " % cutOff)
			return self.cutOff
		except TypeError as err:
			sys.stderr.write("Invalid cut-off value : %s\n" % err)
			return self.cutOff

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


	def validateFilePath(self, filePath, verifyStep=False):
		"""
		Given a file path, checks if it has .list extension and if it is numbered after the titration step.
		If `step` arg is provided, validation will enforce that parsed file number matches `step`.
		Returns the titration step number if found, IOError is raised otherwise
		"""
		try:
			rePath = re.compile(r'(.+/)?(.*[^\d]+)(?P<step>[0-9]+)\.list') # expected path format
			matching = rePath.match(filePath) # attempt to match
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


	def parseTitrationFile(self, titrationFile):
		"""
		Titration file parser.
		Returns a new dict which keys are residues' position and values are AminoAcid objects.
		If residues argument is provided, updates AminoAcid by adding parsed chemical shift values.
		Throws ValueError if incorrect lines are encountered in file.
		"""
		try :
			with open(titrationFile, "r", encoding = "utf-8") as titration:

				# expected line format

				reLine = re.compile(r"^(?P<pos>\d+)N-H\s+(?P<csH>\d+\.\d+)\s+(?P<csN>\d+\.\d+)$")
				reLineIgnore = re.compile(r"^\d.*")

				for lineNb, line in enumerate(titration) :
					line = line.strip()

					# check for ignoring empty lines and header lines
					if reLineIgnore.match(line):

						# attempt to match to expected format
						lineMatch = reLine.match(line)
						if lineMatch: # parse as dict
							chemShift = dict(zip(("position", "chemShiftH", "chemShiftN"),
													lineMatch.groups() ))

							# add or update residue
							if self.residues.get(chemShift["position"]):
								# update AminoAcid object in residues dict
								self.residues[chemShift["position"]].addShift(**chemShift)
							else:
								# create AminoAcid object in residues dict
								self.residues[chemShift["position"]] = AminoAcid(**chemShift)

						else:
							# non parsable, non ignorable line
							raise ValueError("Could not parse file %s at line %s" % (titrationFile, lineNb))

		except (IOError, ValueError) as error:
			sys.stderr.write("%s\n" % error)
			exit(1)


	def plotHistogram (self, step = None, showCutOff = True,
								scale=True, show=True):
		"""
		Define all the options needed (step, cutoof) for the representation.
		Call the getHistogram function to show corresponding histogram plots.
		"""
		if not step: # plot stacked histograms of all steps
			# close stacked hist
			if self.stackedHist and not self.stackedHist.closed:
				self.stackedHist.close()
			# replace stacked hist with new hist
			hist = MultiHist(self.positions,self.intensities)
			self.stackedHist = hist
			self.stackedHist.addCutOffListener(self.setCutOff, mouseUpdateOnly=True)
		else: # plot specific titration step
			# allow accession using python-ish negative index
			step = step if step >= 0 else self.steps + step
			# close existing figure if needed
			if self.hist.get(step) and not self.hist[step].closed:
				self.hist[step].close()
			# plot new hist
			hist = Hist(self.positions, self.intensities[step-1], step=step)
			self.hist[step] = hist
			self.hist[step].addCutOffListener(self.setCutOff, mouseUpdateOnly=True)
		if show:
			hist.show()
		if showCutOff and self.cutOff:
			hist.setCutOff(self.cutOff)
		return hist

	def plotChemShifts(self, residues=None, split = False):
		"""
		Plot measured chemical shifts for each residue as a scatter plot of (chemShiftH, chemShiftN).
		Each color is assigned to a titration step.
		`residue` argument should be an iterable of AminoAcid objects.
		If using `split` option, each residue is plotted in its own subplot.
		"""
		argMap = {
			"all" : self.residues, # might be error prone because of missing data
			"complete" : self.complete,
			"filtered" : self.filtered
			#"selected" : self.selected
		} 
		if residues:
			if argMap.get(residues):
				residueSet = argMap[residues]
			else:
				raise ValueError("Invalid argument : %s" % residues)
		else:
			residueSet = self.complete # using complete residues by default
		fig = plt.figure()

		# set title
		fig.suptitle('Chemical shifts 2D map')
		# set common xlabel and ylabel
		fig.text(0.5, 0.04, 'H Chemical Shift', ha='center')
		fig.text(0.04, 0.5, 'N Chemical Shift', 
				va='center', rotation='vertical')
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
									facecolors='none', cmap=self.colors, c = range(self.steps),
									alpha=0.2)
					#ax.set_title("Residue %s " % res.position, fontsize=10)
					# print xticks as 2 post-comma digits float
					ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
					ax.tick_params(labelsize=8)
				else:
					ax.remove() # remove extra subplots

			# scale
			self.scale_split_shiftmap(residueSet, axes)
			for index, ax in enumerate(axes.flat):
				if index < len(residueSet):
					self.annotateChemShift(residueSet[index], ax)

			# display them nicely
			fig.tight_layout()

			# Add colorbar legend for titration steps using last plot cell data
			fig.subplots_adjust(left=0.15, top=0.85,
								right=0.85,bottom=0.15) # make room for legend
			cbar_ax = fig.add_axes([0.90, 0.15, 0.02, 0.7])
			fig.colorbar(mappable=im, cax=cbar_ax).set_label("Titration steps")

		else: # Trace global chem shifts map
			for residue in residueSet :
				im=plt.scatter(residue.chemShiftH, residue.chemShiftN, 
								facecolors='none', cmap=self.colors, 
								c = range(self.steps), alpha=0.2)
			fig.subplots_adjust(left=0.15, top=0.85,
								right=0.95,bottom=0.15) # make room for legend
			# Add colorbar legend for titration steps
			plt.colorbar().set_label("Titration steps")

		fig.show()
		return fig

	def annotateChemShift(self, residue, ax):
		"Adds chem shift vector and residue position for current residue in current subplot"
		xlim, ylim = ax.get_xlim(), ax.get_ylim()
		xrange = xlim[1] - xlim[0]
		yrange = ylim[1] - ylim[0]
		#print(xrange,yrange)
		x=num.array([1.0,1.0])
		#x=num.array([1.0,1.0])
		k=num.array(residue.arrow[2:])
		#print(x,k)
		x -= x.dot(k) * k / num.linalg.norm(k)**2
		x *= num.array([xrange/yrange, 1.0])
		x /= (num.linalg.norm(x) * 10)
		
		#print(x, sqrt(sum(x ** 2)))
		"""
		ax.arrow(*num.array(residue.arrow[:2]) + x, *residue.arrow[2:],
				head_width=0.07, head_length=0.1, fc='red', ec='red', lw=0.5,
				length_includes_head=True, linestyle='-', alpha=0.7, overhang=0.7)
		"""
		arrowStart = num.array(residue.arrow[:2]) + x
		ax.annotate("", xy=arrowStart + k, xytext=num.array(residue.arrow[:2]) + x,
    		arrowprops=dict(arrowstyle="->", fc="red", ec='red', lw=0.5))
		"""
		ax.arrow(*residue.arrow[:2], *x, head_width=0.02, head_length=0.02, fc='black', ec='green', 
				length_includes_head=True, linestyle=':', alpha=0.6, overhang=0.5)
"""
		horAlign = "left" if x[0] <=0 else "right"
		vertAlign = "top" if x[1] >=0 else "bottom"
		ax.annotate(
			str(residue.position),
			xy=residue.chemShift[0], xytext=residue.chemShift[0]-0.8*x,
			xycoords='data', textcoords='data', fontsize=7,ha=horAlign, va=vertAlign)

	def maxRangeNH(self, residueSet):
		"Returns max range tuple for N and H among residues in residueSet"
		return (max([res.rangeH for res in residueSet]),
				max([res.rangeN for res in residueSet]))

	def scale_split_shiftmap(self, residueSet, axes):
		"Scales subplots when plotting splitted shift map"
		xMaxRange, yMaxRange = num.array(self.maxRangeNH(residueSet)) * 1.5
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

