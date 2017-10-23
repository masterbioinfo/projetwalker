import random
import matplotlib.pyplot as plt
import numpy as num
from math import *
import re
import sys
from classes.AminoAcid import AminoAcid

class Titration (object):
	"""
	Class Titration.
	Contains a list of aminoacid objects and provides methods for accessing each titration step datas.
	"""

	def __init__(self, residues, steps):
		self.residues = residues
		self.complete = [ residue for residue in residues.values() if residue.validate(steps) ]
		self.incomplete = [residue for residue in residues.values() if not residue.validate(steps)]
		self.steps = steps
		self.color = ()
		self._intensities = None

	
	def positions (self, flag = 1):
		if flag == 0:
			target = self.residues
		elif flag == 1:
			target = self.complete
		elif flag == 2:
			target = self.incomplete

		return [ residue.position for residue in target ]

	@property
	def intensities (self):
		if self._intensities is None:
			self._intensities =[ [ residue.chemShiftIntensity[step] for residue in self.complete ] for step in range(self.steps)]
		return self._intensities

	
	def deltaChemShifts (self, flag = 1):
		if flag == 0:
			target = self.residues
		elif flag == 1:
			target = self.complete
		elif flag == 2:
			target = self.incomplete

		return [ residue.deltaChemShift for residue in target ]

	def __getitem__(self, step):
		return (self.positions(), self.intensities[step], self.deltaChemShifts()[step])

	def setHistogram (self, step = None, cutoff = None):
		""" Prend en entrée une titration, l'étape à afficher en histo, le cutoff (pas encore utilisé).
		Define all the options needed (step, cutoof) for the representation.
		Call the getHistogram function to show corresponding histogram plots."""
			
		#print (intensitiesList)
		cutoffList = []
		for aa in self.positions() :
			cutoffList.append (cutoff)

		if step is None: #if step is not precised, all the plots will be showed
		
			#necessary to put before the call to getHistogram because plt.show() stops the sript. 
			#creates a list of cutoff needed to be traced on the plot point (x+1,y+1) after point (x,y)
			for index in range (self.steps): #all the titration steps (the fi
			
			
				plt.subplot(self.steps, 1, index+1)
			

				self.getHistogram (self.positions(), self.intensities[index], cutoffList, index + 1)
				#getHistogram (residuNumberOverCutoff, shiftPerAaOverCutoff, cutoffList, listNumber)
	
		#case : step is mentionned
		else: #checks the value of step
			self.getHistogram (self.positions(), self.intensities[step], cutoffList, step + 1)

		plt.show()

	def getHistogram (self, residuNumberList, shiftPerAa, cutoffList, titrationStep):
		"""Takes a list of residu numbers and a list of their intensities previously calculated per titration step. Shows the corresponding plot.
		In this function remain only graph properties (color, size, abscissa, ordinates) and not any calculation"""

		#ordinatesScale = num.arange(len(shiftPerAa)) #scale for ordinates axe : should be the max of intensity per titration (set arbitrary there)
		colorList = ['orange', 'red', 'green', 'blue', 'purple', 'grey', 'pink', 'yellow', 'cyan', 'brown']
		setColorBar = random.choice(colorList)
		colorList.remove(setColorBar)
		setColorPlot = random.choice(colorList)
		print ('Res :', residuNumberList, 'Shift :',shiftPerAa)
		xAxis = num.array(residuNumberList) #scale for absissa : its length is equal to list of residue length
		shiftPerAa = num.array(shiftPerAa)
		cutoffList = num.array(cutoffList)
		plt.bar(xAxis, shiftPerAa, align = 'center', alpha = 1, color = setColorBar) #set the bar chart ( first arg is the scale for abscissa, alpha is the width of a bar)
		plt.plot (xAxis, cutoffList, color = setColorPlot) #show the cutoff on every graph

		#plt.xticks(residuNumberList, []) #set x ax (second argument prevent to print all residue numbers)
		#print (intensitiesList[10])
		plt.ylabel('Intensity')
		plt.xlabel('Amino Acid')
		plt.ylim(0,1)
		plt.title('Titration step '+str(titrationStep)) #set the title before calling the function because of 'listNumber'



