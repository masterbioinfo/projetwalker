# -*- encoding: utf-8 -*-

"""Module functions uses during Shift2Me works.

Authors : Hermès PARAQUINDES, Louis Duchemin, Marc-Antoine GUENY and Rainier-Numa GEORGES for Dr. Olivier WALKER and Dr. Maggy HOLOGNE 
(ISA-UMR 5280 CNRS,5 Rue de la DOUA, 69100 Villeurbanne -FRANCE). 
This program is developped in Python 3.5.1, Anaconda v5.0.0, JuPyter v5.2.0, MatPlotLib v2.1.0, 
on Ubuntu v16.04.3 LTS (UNIX core system). 
Date of creation : 2017-10-13
Last modification : 2017-10-24."""



###############################################################################################


					### Moduls ###


###############################################################################################

#Moduls used in functions.py.


from classes.AminoAcid import AminoAcid
from math import *
import matplotlib.pyplot as plt
import numpy as num
import pickle
import sys


###############################################################################################


					### Functions ###


###############################################################################################

#All functions used during process are wrote here.

###Fonctions program controls.

def helpOrder():
	"""This functions displays all commands support by the program."""
	
	print("Enter this key word or number to select an order:\n")
	print('1 - Show NMR "2Dmap" globale or not if you select a residu before.')
	print('2 - Select a "cutoff" and aplly its on a plot or all plots.')
	print('3 - Select "help" to show all commands support by Shift2Me.')
	print('4 - Select "histogram" to show all titrations histograms (one histogram per titration).')
	print('5 - Select "load" to load the last job saved.')
	print('6 - Select a "quit" to quit Shift2Me (you can save before quit the program of course).')
	print('7 - Select a "save" to save the current job.')
	print('8 - Select a "select residu" to select a residu to explore him.\n')

	return True


def showCutoff(plotsAndCutoffs):
	""" """
    
	i = 0
	while i < len(plotsAndCutoffs):
		print("Plot {0} have {1} ppm in cutoff.".format(plotsAndCutoffs[i]["plot"], plotsAndCutoffs[i]["cutoff"]))	
		i += 1
	print('To use cutoff function, you must indicate the command, the cutoff selected and the plot affected by the new cutoff (ex: "cutoff 0.5 4").')
    
def cutoffSelection(plotsAndCutoffs, selectOrder):
	"""This function takes plotsAndCutoffs list in argument, she return the new cutoff value (type : float).
	The user can write a new cutoff value. If the cutoff is in acceptable values, the function return 
	the new cutoff value. 
	If the value entry isn't in acceptables values, the function return an error. 
	If the value cannot be transform in float type, the function return an error."""	
	
	#Display all currents plots and their cutoffs.
	
	
	#Select a new cutoff.
	#newCutoff = None
	#while newCutoff == None:
	#	newCutoff = input("What cutoff value do you want applied ?\n")
	
	try :
		newCutoff = float(selectOrder[1])
		if newCutoff <= 2 and newCutoff >= 0:
			print("New cutoff applied = {0}.".format(newCutoff))
			return newCutoff
		elif newCutoff > 2 or newCutoff < 0:
			raise ValueError
		else:
			raise TypeError 
	except TypeError:
		if plotSelected != float :
			print("Cutoff value must be integer or decimal !")
		newCutoff = None	
	except ValueError:
		if newCutoff > 2 :
			print("Cutoff selected is too higher! It's must be lower or equal than 5 !")
		elif newCutoff < 0 :
			print("Cutoff selected is too lower! It's must be higher or equal than 0 !") 
		newCutoff = None


def plotSelection(plotsAndCutoffs, newCutoff, selectOrder):
	"""This function takes plotsAndCutoffs list and newCutoff float in argument, she return the selected plot 
	(type : int).The user can choose the selected plot. Then the function return plotsAndCutoffs list with the 
	new affiliation between plot(s) selectionned and cutoff selectionned previously.
	If the plot is in 0 and the plotsAndCutoffs list length, the function return the selected plot. 
	If the value entry isn't in acceptables values, the function return an error. 
	If the value cannot be transform in integer type, the function return an error. 
	By default, all plots are selected."""
	

	try :
		plotSelected = str(selectOrder[2])
		plotselected = plotSelected.lower()
		
		if plotSelected != "all":
			plotSelected = int(plotSelected)

			if plotSelected  <= len(plotsAndCutoffs) and plotSelected  >= 0:
				plotsAndCutoffs[plotSelected]["cutoff"] = newCutoff
				print("You have selectionned plot n°{0}.".format(plotSelected))
				return plotsAndCutoffs
			else:
				raise ValueError ("The plot choose cannot be selected !") 
				
		elif plotSelected == "all":
			i = 0
			while i < len(plotsAndCutoffs) :
				plotsAndCutoffs[i]["cutoff"] = newCutoff
				i += 1
			print("You have selectionned all plots.")
		else :
			print("Plot cannot be choosen.")

			return plotsAndCutoffs
	except TypeError:
		if plotSelected != int :
			print("Plot selected must be integer !")
		plotSelected = None
	except ValueError:
		if plotSelected > len(plotsAndCutoffs) :
			print("The plot choose cannot be selected !") 
		elif plotSelected < 0 :
			print("Plots numbers cannot be inderior of 0 !")
		plotSelected = None


def quitProgram():
	"""This function allow to quit the program. She takes no argument and return "quit" value. """

	quitMessage = None
	while quitMessage != "yes" and quitMessage != "no": 
		quitMessage = input("Do you want quit this program ? (yes/no)\n")
		try :
			quitMessage = str(quitMessage)
			quitMessage.lower()

			if quitMessage == "yes":
				quit = True
			elif quitMessage == "no":	
				quit = False
			else:
				raise ValueError		
		except ValueError:
			print('Please, would you indicate if you want quit Shift2Me ("yes") or not ("no").')

	return quit


def residuSelection(listResidus):
	"""This function allow to selection a residu. She takes listResidus in argument and return residuSelected.
	If all residus are selected, by default, residuSelected point to listResidus. If a residu is selected,
	residuSelected point to the selected residu."""

	residuSelected = list()

	#Display all residus in the study.
	print("Residus in the study :\n")

	i = 0
	residuInStudy = list()
	while i <len(listResidus):
		residuInStudy.append(listResidus[i].position)
		i += 1
	j = 0

	while j < len(residuInStudy):
		print("{0} : n° residu start line.".format(j))	
		print(residuInStudy[j : j+10])
		j += 10
	print("\nThey are {0} residus in the study.\n".format(i))
		
	#The user can select one or more residu(s).
	nbOfResidusSelected = 0
	while nbOfResidusSelected < 1 or nbOfResidusSelected > len(listResidus) :
		nbOfResidusSelected = input("How many residus would you want select ?\n")
		nbOfResidusSelected  = int(nbOfResidusSelected)
		if nbOfResidusSelected < 1 or nbOfResidusSelected > len(listResidus) :
			print("You can selection a number of residus between 1 and {0}.".format(len(listResidus)))
		elif nbOfResidusSelected >= 1 or nbOfResidusSelected <= len(listResidus) :
			print("You want to selection {0} residus.\n".format(nbOfResidusSelected))

	quantityOfResidusSelected = 1
	residusTotal = nbOfResidusSelected 
	while nbOfResidusSelected != 0 :
		residuSelection = input("Please select a residu. [default: all residus selected]\n")
		residuSelection = str(residuSelection)
		residuSelection = residuSelection.rstrip("N-H")
		residuSelection = residuSelection + "N-H"
	
		if residuSelection == "N-H":
			residuSelected = listResidus
			print("All residus are selected.")
			nbOfResidusSelected = 0
		elif residuSelection != "" and residuSelection in residuInStudy :
			i = 0
			while i <len(listResidus):
				if residuSelection == listResidus[i].position :
					residuSelected.append(listResidus[i])		
					print("{0}/{1} - Residu number {0} are selected !".format(quantityOfResidusSelected, residusTotal, listResidus[i].position))	
					quantityOfResidusSelected += 1	
				i += 1
			nbOfResidusSelected -= 1
		elif residuSelection not in residuInStudy :
			print("This residu is not in the study.")
	
	return residuSelected


###Functions save and load current job.

def saveAsk(directoryIn, datasToBeSave):
	"""This function ask to the user if he want save is current job. She takes directoryIn dictionnary,
	listeFileTitration list, plotsAndCutoffs list and listResidu list of objects, in argument. She return
	"True" if the function has work well.
	If the user want save is current job, it call saveJob function."""

	saveJobAsk = None
	while saveJobAsk != "yes" and saveJobAsk != "no":
		saveJobAsk = input("Do you want save your job ? (yes/no)\n")
		try:
			saveJobAsk = str(saveJobAsk)
			saveJobAsk.lower()
			
			if saveJobAsk == "yes":
				###Save job in progress automatically.
				saveMessage = saveJob(directoryIn, datasToBeSave)
				#saveMessage = jsonSaveJob(directoryIn, datasToBeSave)
				print(saveMessage)
			elif saveJobAsk == "no" :
				print("The current job don't be save.")
			else :
				raise ValueError
		except ValueError:
			print('Please, would you indicate if you want save your current job ("yes") or not ("no").')
			saveJobAsk = None
	return True


def loadAsk():
	"""This function ask to the user if he want load is last job. She takes no argument in argument. 
	She return the list of all elements load from the load file.
	This function can be call after the program is launched."""
	
	loadJobAsk = None
	loadJobAsk = input("Please, indicate a file to load.\n")
	loadJobAsk = str(loadJobAsk)

	elementsLoads = list()

	try :	
		with open(loadJobAsk, 'rb') as loadJobFile:
			my_depickler = pickle.Unpickler(loadJobFile)

			listFileTitration = my_depickler.load()
			elementsLoads.append(listFileTitration)

			plotsAndCutoffs = my_depickler.load()
			elementsLoads.append(plotsAndCutoffs)

			listResidus = my_depickler.load()
			elementsLoads.append(listResidus)

		loadMessage = "Job loads from {0}!".format(loadJobAsk)
		elementsLoads.append(loadMessage)
		return elementsLoads

	except IOError as err:
		sys.stderr.write("%s\n" % err)
		pass


def saveJob(directoryIn, datasToBeSave):
	"""The function can save the job. She takes diretoryIn dictionnary, listFileTitration list, 
	plotsAndCutoffs list and deltaDeltaShifts list in arguments. She return a confirmation message.
	If save cannot save objects in the file, she return an error message."""
	
	try:
		with open("{0}saveJob.txt".format(directoryIn["pathIn"]), 'ab') as saveJobFile:
			my_pickler = pickle.Pickler(saveJobFile)
			my_pickler.dump(datasToBeSave[0])
			my_pickler.dump(datasToBeSave[1])
			my_pickler.dump(datasToBeSave[2])
			my_pickler.dump(datasToBeSave[3])
		return "Job saves in {0}saveJob.txt !".format(directoryIn["pathIn"])

	except IOError as err:
		sys.stderr.write("%s\n" % err)
		exit(1)



def loadJob(directoryIn):
	"""The function can load the last job save. She takes directoryIn dictionnary in argument. She
	return elementsLoads list. This list contains objects loaded from the save file: listFileTitration 
	list, plotsAndCutoffs list and deltaDeltaShifts list.
	This function can be called when the program start in CLI only !"""
	
	elementsLoads = list()

	try :	
		with open("{0}saveJob.txt".format(directoryIn["pathIn"]), 'rb') as loadJobFile:
			my_depickler = pickle.Unpickler(loadJobFile)

			listFileTitration = my_depickler.load()
			elementsLoads.append(listFileTitration)

			plotsAndCutoffs = my_depickler.load()
			elementsLoads.append(plotsAndCutoffs)

			listResidus = my_depickler.load()
			elementsLoads.append(listResidus)

		loadMessage = "Job loads from {0}saveJob.txt !".format(directoryIn["pathIn"])
		elementsLoads.append(loadMessage)
		return elementsLoads
	except IOError as err:
		sys.stderr.write("%s\n" % err)
		exit(1)




