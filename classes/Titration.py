#!/usr/bin/python3
import random
import matplotlib.pyplot as plt
import numpy as num
from math import *
import os, re, sys
from classes.AminoAcid import AminoAcid

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

		## FILE PATH PROCESSING

		# keep track of source data
		self.source = source
		# fetch all .list files in source dir
		if os.path.isdir(source):
			self.files = [ self.source + titrationFile for titrationFile in os.listdir(source) if ".list" in titrationFile ]
		elif type(source) is list: # or use provided source as files
			self.files = source

		# sort files by ascending titration number
		self.files.sort(key=lambda path:self.validateFilePath(path))
		# set number of titration steps including reference step 0
		self.steps  = len(self.files)
		# generate colors for each titration step
		self.colors = plt.cm.get_cmap('hsv', self.steps*2)

		## FILE PARSING
		# init residues {position:AminoAcid object}
		self.residues = dict()
		# and fill it by parsing files
		for titrationFile in self.files:
			self.parseTitrationFile(titrationFile)
		# filter complete residues as list
		self.complete = sorted([ residue for residue in self.residues.values() if residue.validate(self.steps) ], key=lambda a: a.position)
		# incomplete residues
		self.incomplete = set(self.residues) - set(self.complete)
		print("Found %s residues with incomplete data" % len(self.incomplete), file=sys.stderr)
		# Prepare (position, chem shift intensity) coordinates.
		self.intensities = []
		self.positions = [ residue.position for residue in self.complete ]
		for step in range(self.steps - 1): # intensity is null for reference step
			self.intensities.append( [ residue.chemShiftIntensity[step] for residue in self.complete ] )
		self.deltaChemShift = [ residue.deltaChemShift for residue in self.complete ]
		
	def validateFilePath(self, filePath):
		"""
		Given a file path, checks if it has .list extension and if it is numbered after the titration step. 
		Returns the titration step number if found, IOError is raised otherwise
		"""
		try: 
			rePath = re.compile(r'(.+/)?(.+)(?P<step>\d+)\.list') # expected path format
			matching = rePath.match(filePath) # attempt to match
			if matching:
				# retrieve titration step number
				fileNumber = int(matching.group("step")) 
				return fileNumber
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
				for lineNb, line in enumerate(titration) :
					# check for empty lines and header lines
					if line.strip() and not line.strip().startswith("Assignment"):
						lineMatch = reLine.match(line.strip()) # attempt to match to expected format
						if lineMatch: # parse line as dict 
							chemShift = dict(zip(
								("position", "chemShiftH", "chemShiftN"),
								lineMatch.groups() )) 
							if self.residues.get(chemShift["position"]): # update AminoAcid object in residues dict
								self.residues[chemShift["position"]].addShift(**chemShift)
							else: # create AminoAcid object in residues dict
								self.residues[chemShift["position"]] = AminoAcid(**chemShift)
						else:
							raise ValueError("Could not parse file %s at line %s" % (titrationFile, lineNb))
		except (IOError, ValueError) as error:
			sys.stderr.write("%s\n" % error)
			exit(1)

	def plotHistogram (self, step = None, cutOff = None, scale=True):
		""" 
		Define all the options needed (step, cutoof) for the representation.
		Call the getHistogram function to show corresponding histogram plots.
		"""
		if step is None: #if step is not precised, all the plots will be showed
			# split figure in `steps` rows
			fig, axes = plt.subplots(nrows=self.steps-1, ncols=1, sharex=True, sharey=True, squeeze=True, subplot_kw=None, gridspec_kw=None)
			fig.suptitle('Titration : steps 1 to %s' % self.steps) # set title
			fig.text(0.04, 0.5, 'Chem Shift Intensity', va='center', rotation='vertical') # set common ylabel
			for index, ax in enumerate(axes): # first titration step has no intensity values
				if scale:
					# Set histograms scale using max intensity value
					ax.set_ylim(0, num.round(num.amax(self.intensities) + 0.05, decimals=1))
				self.setHistogram (ax, index, cutOff)
		# plot specific titration step
		else:
			fig = plt.figure()
			main = fig.add_subplot(111)
			self.setHistogram(main, step, cutOff)
			main.set_title('Titration step %s' % step) 
			plt.ylabel('Chem Shift Intensity')
		plt.xlabel('Residue') # set common xlabel
		# set plot ticks
		plt.xticks(range(self.positions[0] - self.positions[0] % 5, self.positions[-1] + 10, 10))
		plt.show()

	def setHistogram (self, ax, step, cutOff = None):
		"""
		Takes a list of residu numbers and a list of their intensities previously calculated per titration step. Shows the corresponding plot.
		In this function remain only graph properties (color, size, abscissa, ordinates) and not any calculation"""

		#colorBar = self.colors(step*2)
		xAxis = num.array(self.positions)
		yAxis = num.array(self.intensities[step])
		barList = ax.bar(xAxis, yAxis, align = 'center', alpha = 1)
		if cutOff: # show the cutoff on every graph
			for bar in barList:
				if bar.get_height() > cutOff:
					bar.set_color('orange')
			ax.axhline(cutOff, color = "red", linewidth=0.5, linestyle='--')
		
		