# -*- encoding: utf-8 -*-
"""
Module functions, classes and methods use during Shift2Me works.

Authors : Hermès PARAQUINDES, Louis Duchemin, Marc-Antoine GUENY and Rainier-Numa GEORGES for Dr. Olivier WALKER and Dr. Maggy HOLOGNE (ISA-UMR 5280 CNRS,5 Rue de la DOUA, 69100 Villeurbanne -FRANCE). This program is developped in Python 3.5.1, date of creation : 2017-10-13, last modification : 2017-10-16.
"""



###############################################################################################


					### Moduls ###


###############################################################################################

#Moduls used in methods.py.

import matplotlib.pyplot as plt
import numpy as num
from math import *
import re
import sys
from classes.AminoAcid import AminoAcid

###############################################################################################


					### Functions ###


###############################################################################################

#All functions used during process are wrote here.



def validateFilePath(filePath):
	"""
	Given a file path, checks if it has .list extension and if it is numbered after the titration step. 
	Returns the titration step number if found, IOError is raised otherwise
	"""
	try: 
		rePath = re.compile(r'(.+/)?(.+)(?P<step>\d+)\.list') # expected path format
		matching = rePath.match(filePath) # attempt to match
		if matching:
			fileNumber = int(matching.group("step")) # retrieve titration step number
			return fileNumber
		else:
			raise IOError("Refusing to parse file %s : please check it is named like *[0-9]+.list" % path)
	except IOError as err: 
		sys.stderr.write("%s\n" % err )
		exit(1)

def sortPath(pathList):
	"""
	Iterates over a list of file path, calling validateFilePath() and using its return value as sort key. 
	Returns sorted file path according to titration step number. 
	"""
	return sorted(pathList, key=lambda path:validateFilePath(path))			

def parseTitrationFile(titrationFile, residues=dict()):
	"""
	Titration file parser. 
	Returns a new dict which keys are residues' position and values are AminoAcid objects.
	If residues argument is provided, updates AminoAcid by adding parsed chemical shift values.
	Throws ValueError if incorrect lines are encountered in file. 
	"""

	try :
		with open(titrationFile, "r", encoding = "utf-8") as titration:
			reLine = re.compile(r"^(?P<pos>\d+)N-H\s+(?P<csH>\d+\.\d+)\s+(?P<csN>\d+\.\d+)$") # expected line format
			for lineNb, line in enumerate(titration) :
				if line.strip() and not line.strip().startswith("Assignment"): # check for empty lines and header lines
					lineMatch = reLine.match(line.strip()) # attempt to match to expected format
					if lineMatch:
						chemShift = dict(zip(
							("position", "chemShiftH", "chemShiftN"),
							lineMatch.groups() )) # parse line as dict 
						if residues.get(chemShift["position"]): # update AminoAcid object in residues dict
							residues[chemShift["position"]].addShift(**chemShift)
						else: # create AminoAcid object in residues dict
							residues[chemShift["position"]] = AminoAcid(**chemShift)
					else:
						raise ValueError("Could not parse file %s at line %s" % (titrationFile, lineNb))
		return residues
	except (IOError, ValueError) as error:
		sys.stderr.write("%s\n" % error)
		exit(1)


def calculateRelativesShifts(listChemicalShift):
	"""This function takes in argument listChemicalShift list of all residus retained in the study.
	She return the same list with all relatives chemicals shifts.
	The function calculate for all residus and all N15 and H1 atoms :
		relativeChemicalShift = chemicalShift([B protein] = i) - chemicalShift([B protein] = 0)"""
	
	i = 1
	while i < len(listChemicalShift):
		j = 0
		while j < len(listChemicalShift[i]):
			listChemicalShift[i][j]["chemicalShiftN"] = float(listChemicalShift[i][j]["chemicalShiftN"]) - float(listChemicalShift[0][j]["chemicalShiftN"])
			listChemicalShift[i][j]["chemicalShiftH"] = float(listChemicalShift[i][j]["chemicalShiftH"]) - float(listChemicalShift[0][j]["chemicalShiftH"])
			j += 1
		i += 1
	return listChemicalShift


def deltaDeltaChemicalsShifts(listChemicalShift):
	"""This function takes in argument listChemicalShift list of all relatives chemicals shifts.
	She return an other list named deltaDeltaShifts who contains delta(residusChemicalsShifts).
	The function calculate deltas of chemicals shifts for all residus :
		delta(residusChemicalsShifts = sqrt((relativesHChemicalShifts) ** 2 + ((relativesNChemicalShifts)/5) ** 2)"""

	i = 1
	deltaDeltaShifts = list()
	while i < len(listChemicalShift):
		j = 0
		titrationShift = list()
		while j < len(listChemicalShift[i]):
			deltaDeltaShift = {"residue": None,"deltaDeltaChemicalShift": None}

			deltaDelta = sqrt((listChemicalShift[i][j]["chemicalShiftH"]**2)+((listChemicalShift[i][j]["chemicalShiftN"]/5)**2))

			deltaDeltaShift ["residue"] = listChemicalShift[i][j]["residue"]
			deltaDeltaShift ["deltaDeltaChemicalShift"] = deltaDelta

			titrationShift.append(deltaDeltaShift)
			j += 1
		deltaDeltaShifts.append(titrationShift)
		i += 1
	return deltaDeltaShifts


def cutoffSelection():
	"""This function takes no argument, she return the new cutoff value (type : float).
	The user can write a new cutoff value. If the cutoff is in acceptable values, the function return 
	the new cutoff value. 
	If the value entry isn't in acceptables values, the function return an error. 
	If the value cannot be transform in float type, the function return an error."""	

	newCutoff = input("What cutoff value do you want applied ?\n")
	
	try :
		newCutoff = float(newCutoff)
		if newCutoff <= 5 and newCutoff >= 0:
			print("New cutoff applied = {0}.".format(newCutoff))
			return newCutoff
		else:
			if newCutoff > 5 :
				raise ValueError ("Cutoff selected is too higher! It's must be lower or equal than 5 !") 
			elif newCutoff < 0 :
				raise ValueError ("Cutoff selected is too lower! It's must be higher or equal than 0 !") 
	except TypeError:
		if plotSelected != float :
			print("Cutoff value must be integer or decimal !")


def plotSelection(deltaDeltaShifts):
	"""This function takes deltaDeltaShifts list in argument, she return the selected plot (type : int).The user 
	can choose the selected plot. 
	If the plot is in 0 and the deltaDeltaShifts list length, the function return the selected plot. 
	If the value entry isn't in acceptables values, the function return an error. If the value cannot 
	be transform in integer type, the function return an error. 
	They are an exception if the user write "all", or "All", or "ALL", in this case, the user
	selected all plots."""

	plotSelected = input('Which plot do you want to select ?\nEnter "all" to selection all plots.\n')
	
	try :
		if plotSelected != "all" :
			plotSelected = int(plotSelected)
	
			if plotSelected  <= len(deltaDeltaShifts) and plotSelected  >= 0:
				print("You selectionned plot n°{0}.".format(plotSelected))
				return plotSelected
			else:
				if plotSelected > len(deltaDeltaShifts) :
					raise ValueError ("The plot choose cannot be selected !") 
				elif plotSelected < 0 :
					raise ValueError ("Plots numbers cannot be inderior of 0 !") 
		elif plotSelected == "all" or plotSelected == "All" or plotSelected == "ALL" :
			plotSelected.lower()
			print("You selectionned all plots.")
			return plotSelected
	except TypeError:
		if plotSelected != int :
			print("Plot selected must be integer !")
	except ValueError:
		if plotSelected != "all":
			print('Enter "all" to selection all plots.')

def graph (deltaDeltaShifts, cutOff):
	print (cutOff)
	listNumber = 0
	#plt.subplots(2, 2)
	for listChemicalShift in deltaDeltaShifts :
		listNumber += 1
		values = []
		aminoAcid = []
		print (listChemicalShift,'\n\n\n\n')
		for index in range (0, len(listChemicalShift)):
			if listChemicalShift[index]['deltaDeltaChemicalShift'] >= cutOff:
				values.append(listChemicalShift[index]['deltaDeltaChemicalShift'])
				aminoAcid.append(listChemicalShift[index]['residue'].rstrip('N-H'))
		number = len(values)
		scale = num.arange(number)
		plt.subplot(int(str(int(len(deltaDeltaShifts)/2+0.5))), 2, listNumber)
		plt.bar(scale, values, align='center', alpha=1)
		plt.xticks(scale, aminoAcid)
		plt.ylabel('Intensity')
		plt.xlabel('Amino Acid')
		axes = plt.gca()
		axes.xaxis.set_tick_params(labelsize = 5)
		plt.title('Delta Delta'+str(listNumber))
	
	plt.show()

def setHistogram (aaList, step, cutoff):
	if step is None:
		aminoAcidList = []
		intensitiesList = []
		for titrationStep in aaList:
			aminoAcidList.append(titrationStep.position)
			intensitiesList.append(titrationStep.chemShiftN)
		print (intensitiesList)
		getHistogram (aminoAcidList, intensitiesList)
			
		
		


def getHistogram (aminoAcidList, intensitiesList):
		print ('\n',aminoAcidList,'\n')
		scale = 0
		listNumber = 0
		for index in range (0, len(intensitiesList[0])):
			listNumber += 1
			
			shiftPerAa = []
			for intensityStep in intensitiesList:
				shiftPerAa.append(intensityStep[index])
			
			scale = num.arange(len(shiftPerAa))
			scale2 = num.arange(len (aminoAcidList))
			plt.bar(scale, shiftPerAa, align ='center', alpha = 1)
			plt.xticks(scale2, [])
			plt.subplot (round(len(intensitiesList)/2), 2, listNumber)
		print (listNumber)
			
			
		plt.show()
	



