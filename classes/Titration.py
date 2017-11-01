#!/usr/bin/python3

"""
Titration class module

Titration allows manipulating chemical shift data measured with 2D NMR
Input is a set of `.list` tabular files with one residue per line, e.g output of Sparky
It calculates chemical shift variation at each titration step using the first step as reference.
They are transformed into a single 'intensity' value, associated to a residue. 
The class provides matplotlib wrapping functions, allowing to display the data from the analysis, 
as well as setting an cut off to filter residues having high intensity values.
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


def saveGraph (name, format = 'png'):
	"""Saves graphs with a specific name for each figure. 
	Default format is png but can be changed into pdf, ps, eps and svg.
	Creates a repository named 'results' to store all figures.
	"""
	if not os.path.exists("results/"):
		os.makedirs("results/")
	print ("New figure saved at", "results/" + name + "." + format + "\n")
	return plt.savefig("results/" + name + "." + format, format = format)

class Titration (object):
	"""
	Class Titration.
	Contains a list of aminoacid objects
	Provides methods for accessing each titration step datas.
	"""

	def __init__(self, source):
		"""
		Load titration files, check their integrity
		`source` is either a directory containing `.list` file, or is a list of `.list` files
		Separate complete vs incomplete data
		"""

		# Placeholder for naming saved titrations
		self.name = None

		## FILE PATH PROCESSING

		# keep track of source data
		self.source = source
		
		# fetch all .list files in source dir
		if type(source) is list: # or use provided source as files
			self.files = source
		elif os.path.isdir(source):
			self.files = [ os.path.join(self.source, titrationFile) for titrationFile in os.listdir(source) if ".list" in titrationFile ]
		elif os.path.isfile(source):
			return self.load(source)

		# sort files by ascending titration number
		self.files.sort(key=lambda path:self.validateFilePath(path))
		
		# set number of titration steps including reference step 0
		self.steps  = len(self.files)
		
		# generate colors for each titration step
		self.colors = plt.cm.get_cmap('hsv', self.steps)

		## FILE PARSING

		# init residues {position:AminoAcid object}
		self.residues = dict()
		
		# and fill it by parsing files
		for titrationFile in self.files:
			print("Loading file %s" % titrationFile, file=sys.stderr)
			self.parseTitrationFile(titrationFile)
		
		# filter complete residues as list and sort them by positions
		self.complete = sorted([ residue for residue in self.residues.values() if residue.validate(self.steps) ], key=lambda a: a.position)
		
		# incomplete residues
		self.incomplete = set(self.residues.values()) - set(self.complete)

		print("Found %s residues out of %s with incomplete data" % (len(self.incomplete), len(self.complete)), file=sys.stderr)
		
		# Prepare (position, chem shift intensity) coordinates for histogram plot
		self.intensities = [] # 2D array, by titration step then residu position
		self.positions = []
		self.deltaChemShift = []
		for step in range(self.steps - 1): # intensity is null for reference step
			self.intensities.append( [ residue.chemShiftIntensity[step] for residue in self.complete ] )
		for residue in self.complete:
			self.positions.append(residue.position)
			self.deltaChemShift.append(residue.deltaChemShift)

		## PLOTTING

		self.cutOff = None
		self.positionTicks =range(self.positions[0] - self.positions[0] % 5, self.positions[-1] + 10, 10)
		self.stackedHist=MultiHist(self.positions,self.intensities)
		self.hist = dict()

	@property
	def sortedSteps(self):
		return sorted(range(1,self.steps))

	def setCutOff(self, cutOff):
		for hist in self.hist.values():
			self.hist.setCutOff(cutOff)
		self.stackedHist.setCutOff(cutOff)


	def validateFilePath(self, filePath):
		"""
		Given a file path, checks if it has .list extension and if it is numbered after the titration step. 
		Returns the titration step number if found, IOError is raised otherwise
		"""
		try: 
			rePath = re.compile(r'(.+/)?(.*[^\d]+)(?P<step>[0-9]+)\.list') # expected path format
			matching = rePath.match(filePath) # attempt to match
			if matching:
				# retrieve titration step number parsed from file name
				return int(matching.group("step")) 
			else:
				# found incorrect line format
				raise IOError("Refusing to parse file %s : please check it is named like *[0-9]+.list" % path)
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


	def plotHistogram (self, step = None, cutOff = None, scale=True, show=True):
		""" 
		Define all the options needed (step, cutoof) for the representation.
		Call the getHistogram function to show corresponding histogram plots.
		"""
		if not step: #if step is not precised, all the plots will be showed
			targetHist = self.stackedHist
		else: # plot specific titration step
			if not self.hist.get(step):
				self.hist[step] = Hist(self.positions, self.intensities[step-1], step=step)
			targetHist = self.hist[step]
		if show:
			targetHist.show()
		if cutOff:
			targetHist.setCutOff(cutOff)
		return targetHist



	def plotChemShifts(self, residues=None, split = False):
		"""
		Plot measured chemical shifts for each residue as a scatter plot of (chemShiftH, chemShiftN).
		Each color is assigned to a titration step.
		`residue` argument should be an iterable of AminoAcid objects.
		If using `split` option, each residue is plotted in its own subplot.
		"""
		residueSet = residues or self.complete # using complete residues by default
		fig = plt.figure()
		
		# set title
		fig.suptitle('2D map of chemical shifts')
		
		if split:
			# create an array of cells with squared shape
			axes = fig.subplots(nrows=ceil(sqrt(len(residueSet))), 
								ncols=round(sqrt(len(residueSet))), 
								sharex=False, sharey=False, squeeze=True)
			
			# set common xlabel and ylabel
			fig.text(0.5, 0.04, 'H Chemical Shift', ha='center') 
			fig.text(0.04, 0.5, 'N Chemical Shift', va='center', 
					rotation='vertical') 

			# iterate over each created cell
			for index, ax in enumerate(axes.flat):
				if index < len(residueSet):
					# Trace chem shifts for current residu in new graph cell
					im = ax.scatter(residueSet[index].chemShiftH, residueSet[index].chemShiftN, 
									facecolors='none', cmap=self.colors, c = range(self.steps), 
									alpha=0.2)
					ax.set_title("Residue %s " % residueSet[index].position)
					ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
				else:
					ax.remove() # remove extra subplots

			# display them nicely
			fig.tight_layout()

			# Add colorbar legend for titration steps using last plot cell data
			fig.subplots_adjust(left=0.15, top=0.85, 
								right=0.85,bottom=0.15) # make room for legend
			cbar_ax = fig.add_axes([0.90, 0.15, 0.02, 0.7])
			fig.colorbar(mappable=im, cax=cbar_ax).set_label("Titration steps")

		else:
			for residue in residueSet : 
				# Trace global chem shifts map
				im=plt.scatter(residue.chemShiftH, residue.chemShiftN, facecolors='none', cmap=self.colors, c = range(self.steps), alpha=0.2)
			
			# Add colorbar legend for titration steps
			plt.colorbar().set_label("Titration steps")
		
		fig.show()

	def extractResidues (self, cutOff = 0, targetFile = 'extracted_residues.txt', stepBegin = 'last', stepEnd = 'last'):
		"""
		Enables the extraction of residues whose intensity at the last step (default) is superior or equal to the cutoff (by default equal to 0).
		Takes attiuts of Titration object, optinal cutOff, targetFile, titration step to begin with (stepBegin) and to end with (stepEnd).
		Both stepBegin and stepEnd represent an interval with included limits. 
		For example: stepBegin = 1, stepEnd = 2 means from step 1 (included) to step 2 (included).
		Create and write in a file (extracted_residues.txt by default) the positions of residues as well as their intensity for each titration
		Returns a list of residues potentially involved in interaction (can be given as an argument to plotChemShifts())
		"""		
		try:
			#First stage of argument conformity checking
			if stepBegin == 'all' or stepEnd == 'all':
				stepBegin = 1
				stepEnd = self.steps-1
			elif stepBegin == 'last' or stepEnd == 'last':
				stepBegin = int(self.steps-1)
				stepEnd = int(self.steps-1)
			elif type(stepBegin) != int or type(stepEnd) != int:
					raise TypeError ("Enter an integer between 1 and", self.steps-1)
			else:
				if stepEnd > (self.steps-1):
					stepEnd = self.steps-1
				if stepBegin > (self.steps-1):
					stepBegin = self.steps-1
			
			#Extraction stage
			if stepBegin <= 0 or stepEnd <= 0:
				raise ValueError ("Titration steps begin with 1 and end with", self.steps-1 )
			else :
				print ("Extracting residues using intenisties provided from step", stepBegin, "to step", stepEnd, "\n")
				titrationList = []
				[ titrationList.append("Titration " + str(index)) for index in range (1, self.steps) ] #list to be written in the new file
				if cutOff == 0: #cutoff not mentionned
						print("All residues will be extracted")
				#Write the header at first
				with open(targetFile, 'w') as f:
					f.write ("Residue" + "\t" + "\t".join(titrationList) + "\n")
				f.close()
				#Then write the content
				interactionResidues = []
				with open(targetFile, 'a') as f:
					for residue in self.complete:
						for intensity in residue.chemShiftIntensity[stepBegin-1:stepEnd]:
							if intensity >= cutOff and residue not in interactionResidues:
								# join separates a list of strings into elements separates by "\t" (in this case)
								# map converts each element of a list into a string (in this case)
								f.write(str(residue.position) + "\t" + "\t".join(map(str,residue.chemShiftIntensity)) + "\n")
								interactionResidues.append(residue)  
				f.close()
				print ("Residues saved in the file : " + str(targetFile) + "\n")
				return interactionResidues
		except (ValueError, TypeError) as error:
			sys.stderr.write("%s\n" % error)
			exit(1)


	def save(self, path):
		"Save method for titration object"
		try:
			stackedHist = self.stackedHist
			hist = self.hist
			self.stackedHist= None
			self.hist = dict()
			with open(path, 'wb') as saveHandle:
				pickle.dump(self, saveHandle)

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

