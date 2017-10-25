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
import json
from math import *
import matplotlib.pyplot as plt
import numpy as num
import pickle
import sys


###############################################################################################


					### Functions ###


###############################################################################################

#All functions used during process are wrote here.



###Functions files verifications.
def informationsFile(listFileTitration):
	"""The fonction takes the all path of the file. Then she return the path without the file's name (pathIn), 
	the file's name(fileNameOpen), the file's extension (extensionIn) in the dictionary named "directory". 
	Also, she test if the file name is ".list" or "txt". If it's not the case, she return an error."""

	try:
		for fileInformations in listFileTitration:
			directory = {"pathIn" : None, "fileNameOpen": None, "extensionIn": None}
			fileInformations = fileInformations.split(".")
			directory["extensionIn"] = fileInformations[1]	
		
			#If openFile have ".list" or ".txt" extension :
			if directory["extensionIn"] == "list" or directory["extensionIn"] == "txt" :	
				fileInformations = str(fileInformations[0]).split("/")
				directory["fileNameOpen"] = fileInformations[-1]
				i = 0
				path = ""
			
				#Reformating open file's path :
				while i < len(fileInformations) - 1 :
					path = path + "{0}/".format(fileInformations[i])
					i += 1 
				directory["pathIn"] = path
			
			#If open file haven't ".list"or ".txt" extension :
			else :
				raise IOError("Le fichier {0} n'a pas d'extension '.list' ou '.txt'.".format(fileInformation))

		return directory
	except IOError as err:
		sys.stderr.write("%s\n" % err)
		exit(1)

def formatVerification(listFileTitration):
	"""The fonction takes the list who contained all files's paths. She test all files. If a file ".list" is in the good format,
	she return True. In other case, she return an error with the file's name. To do that, the file tested must be open, her first 
	three lines are parsed and then tested on seven marks."""

	try:
		for titrationFile in listFileTitration :
			testFileArray = list()			#Takes the first three lines of each file to test if the file have a good format.
			with open(titrationFile, "r", encoding = "utf-8") as f:
				testFile = f.readlines(50)		#Reads the first three lines of each files. 

				for testLine in testFile :
					testLine = (testLine.strip("\n").strip(" ")).split("\t")
					testLine = str(testLine)
					testLine = testLine.strip("['").strip("']")
					testLine = testLine.split(" ")
					testFileArray.append(testLine)
		
			#Test if the file have a good format under seven marks :
		if testFileArray[0][0] == "Assignment" and testFileArray[0][9] == "w1" and testFileArray[0][18] == "w2" and testFileArray [1][0] == "" and testFileArray [2][0] != "" and testFileArray [2][4] != "" and testFileArray [2][10] != "" :
			testFileArray = True

	except IOError as err:
		sys.stderr.write("%s\n" % err)
		exit(1)



###Function parse files.

def parseTitrationFile(titrationFile, listChemicalShift, residusForgetted, missingDatas, residusNotRetained):
	"""This function takes in arguments: the file's path (titrationFile), the list who will contains all chemicals 
		shifts after parsing(listChemicalShift), the path of the file who contains all residu not retained in the study,
		the variable missingDatas, and the list of all residus not retained in the study because they don't
		have all chemicals shifts (residusNotRetained).

	In a first time, the file passed in argument, is open and parsed line after line.
	In a second time, if missingDatas = True, so we search all resdus without all chemicals shifts (one missing). If the line
		tested reveals one chemical shift is missing, then this residus is write in the not retained residus's file and
		in residusNotRetained list. In the other case, nothing his write and we pass to next the line of the file parsed.
	In a third time, if missingDatas = False, we want takes only residus who have all chemicals shifts in all files parsed.
		First of all, we write the line parsed in listChemicalShiftParsed list, then we test if this last residus is write
		in residusNotRetained list. If he's write on this list, we deleted this residu. In the other case, we keep this 
		residus in listChemicalShiftParsed list. 
	In a the last step, listChemicalShiftParsed list appends listChemicalShift list, this last list will be return.

	In all case, if the line parsed is the first or the second of the file parsed, so we pass her. If the line isn't in a good
	format, so an error is returned."""

	try :
		with open(titrationFile, "r", encoding = "utf-8") as f:

			listChemicalShiftParsed = list()
			for line in f :
		
				chemicalShiftAssignements  = {"residue": None ,"chemicalShiftN": None ,"chemicalShiftH": None}		

				chemicalShift = (line.strip("\n").strip(" ")).split("\t")
				chemicalShift = str(chemicalShift)
				chemicalShift = chemicalShift.strip("['").strip("']")
				chemicalShift = chemicalShift.split(" ")

				#In a first time, we search residus without all chemicals shifts.
				if missingDatas == True :
					#If the residu don't have all informations and doesn't write in residusNotRetained list yet, we write him in the list.
					if chemicalShift[0] != "Assignment" and chemicalShift[0] != "" and ((chemicalShift[4] == "" or len(chemicalShift) < 10) or (chemicalShift[4] == "0.00000" or chemicalShift[10] == "0.000")):
							listChemicalShiftParsed.append(chemicalShift[0])
							aaNotRetained = "{0}\t{1}\n".format(titrationFile, chemicalShift[0]) 
							with open(residusForgetted, "a") as fileAaNotRetained:
								fileAaNotRetained.write(aaNotRetained + "\n")
								fileAaNotRetained.close()

				#In a second time, we don't search residu without all chemicals shifts, we search residus with all informations.
				elif missingDatas == False :
					#Line in the header aren't retained.
					if chemicalShift[0] == "Assignment" or chemicalShift[0] == "" :
						pass
					#Residus without all chemicals shifts are not retained.
					elif chemicalShift[4] == "" or len(chemicalShift) < 10 or chemicalShift[4] == "0.00000" or chemicalShift[10] == "0.000" :
						pass
					#We search if residu with all chemicals shifts are in residusNotRetained list or not.
					elif chemicalShift[4] != "" and chemicalShift[10] != "" :
						chemicalShiftAssignements["residue"] = chemicalShift[0]
						chemicalShiftAssignements["chemicalShiftN"] = chemicalShift[4]
						chemicalShiftAssignements["chemicalShiftH"] = chemicalShift[10]
						listChemicalShiftParsed.append(chemicalShiftAssignements)
						#We test only the last residu write in listChemicalShift.
						#If this is write in residusNotRetained list, we delete him.
						for titration in residusNotRetained :
							for residu in titration :
								if residu == chemicalShift[0] :
									del listChemicalShiftParsed[-1]
							
					#If other line, not planned in the file, are presents the program print a message error.
					else :
						raise ValueError

		listChemicalShift.append(listChemicalShiftParsed)

		return listChemicalShift
			
	except IOError as err:
		sys.stderr.write("%s\n" % err)
		exit(1)
	except ValueError :
		print("A line in {0} isn't in support format (.list).".format(titrationFile))


###Functions objects creation.

def aminoAcideObjectsCreation(listChemicalShift):
	"""This function takes listChemicalShiftinargument (list) and return listResidu (list).
	It allow to create AminoAcid object with all informations contains in listChemicalShift.
	Each object are create with a position argument, a list of all chemicals shifts of the residu's
	hydrogen, another list of all chemicals shifts of the residu's nitrogen."""

	listResidus = list()
	for chemicalShift in listChemicalShift[0]:
		residu = AminoAcid(**chemicalShift)
		listResidus.append(residu)
	#Add all chemShiftH and chemShiftN for each residu.
	i = 1 
	while i < len(listChemicalShift):
		j = 0
		while j < len(listChemicalShift[i]):
			listResidus[j].chemShiftH.append(float(listChemicalShift[i][j]["chemicalShiftH"]))
			listResidus[j].chemShiftN.append(float(listChemicalShift[i][j]["chemicalShiftN"]))
			j += 1
		i += 1
	return listResidus



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


def cutoffSelection(plotsAndCutoffs):
	"""This function takes plotsAndCutoffs list in argument, she return the new cutoff value (type : float).
	The user can write a new cutoff value. If the cutoff is in acceptable values, the function return 
	the new cutoff value. 
	If the value entry isn't in acceptables values, the function return an error. 
	If the value cannot be transform in float type, the function return an error."""	
	
	#Display all currents plots and their cutoffs.
	i = 0
	while i < len(plotsAndCutoffs):
		print("Plot {0} have {1} ppm in cutoff.".format(plotsAndCutoffs[i]["plot"], plotsAndCutoffs[i]["cutoff"]))	
		i += 1
	
	#Select a new cutoff.
	newCutoff = None
	while newCutoff == None:
		newCutoff = input("What cutoff value do you want applied ?\n")
	
		try :
			newCutoff = float(newCutoff)
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


def plotSelection(plotsAndCutoffs, newCutoff):
	"""This function takes plotsAndCutoffs list and newCutoff float in argument, she return the selected plot 
	(type : int).The user can choose the selected plot. Then the function return plotsAndCutoffs list with the 
	new affiliation between plot(s) selectionned and cutoff selectionned previously.
	If the plot is in 0 and the plotsAndCutoffs list length, the function return the selected plot. 
	If the value entry isn't in acceptables values, the function return an error. 
	If the value cannot be transform in integer type, the function return an error. 
	By default, all plots are selected."""
	
	plotSelected = None
	while plotSelected == None :
		plotSelected = input('Which plot do you want to select ? [default : all] \n')

		try :
			if plotSelected:
				plotSelected = int(plotSelected)
	
				if plotSelected  <= len(plotsAndCutoffs) and plotSelected  >= 0:
					plotsAndCutoffs[plotSelected]["cutoff"] = newCutoff
					print("You have selectionned plot n°{0}.".format(plotSelected))
					return plotsAndCutoffs
				else:
					raise ValueError ("The plot choose cannot be selected !") 
					 
			else:
				i = 0
				while i < len(plotsAndCutoffs) :
					plotsAndCutoffs[i]["cutoff"] = newCutoff
					i += 1
				print("You have selectionned all plots.")

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
					print("{0}/{1} - Residu number {2} are selected !".format(quantityOfResidusSelected, residusTotal, listResidus[i].position))	
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


def jsonSaveJob(directoryIn, listFileTitration, plotsAndCutoffs, listResidus):
	"""This function takes directoryIn and plotsAndCutoffs dictionnaries, plus listFileTitration
	and deltaDeltaShifts lists. She allow to save listeFileTitration, plotsAndCutoffs and delatDeltaShifts
	at json format. She return a confirmation message. In the other case, she return a message error."""

	try:
		datasSave = [listFileTitration, plotsAndCutoffs, listResidus]
		with open("{0}saveJob.json".format(directoryIn["pathIn"]), 'w') as saveJobFile:
			saveJobFile.write(json.dumps(datasSave, indent=5))
		return "Job saves in {0}saveJob.json !".format(directoryIn["pathIn"])

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


def jsonLoadJob(directoryIn):
	"""This function takes directoryIn dictionnay in argument and return datasLoad list who contains
	all element saved in the save file at json format : listeFileTitration, plotsAndCutoffs, 
	deltaDeltaShifts. Plus, the function return a confirmation message.
	In the other case, she return a message error.
	This function can be called when the program start in CLI only !"""

	try:
		with open("{0}saveJob.json".format(directoryIn["pathIn"]), 'r') as loadJobFile:
			datasLoad = json.load(loadJobFile) 
		loadMessage = "Job loads from {0}saveJob.json !".format(directoryIn["pathIn"])
		datasLoad.append(loadMessage)
		return datasLoad
	except IOError as err:
		sys.stderr.write("%s\n" % err)
		exit(1)	


###Functions plots generation.

def histograms(deltaDeltaShifts, plotsAndCutoffs):
	""" """

	print (cutOff)
	listNumber = 0
	scale = None
	#plt.subplots(2, 2)
	for listChemicalShift in deltaDeltaShifts :
		listNumber += 1
		intensities = [] # ordonnees
		aminoAcid = [] # residues
		print (listChemicalShift,'\n\n\n\n')
		for index in range (len(listChemicalShift)):
			intensities.append(listChemicalShift[index]['deltaDeltaChemicalShift'])
			aminoAcid.append(listChemicalShift[index]['residue'].rstrip('N-H'))
			if max(intensities) > scale:
				scale = num.arange(max(intensities)) # Set scale after max value
		plt.subplot(round(len(deltaDeltaShifts)/2), 2, listNumber) # set subplots arrangement
		plt.bar(scale, intensities, align='center', alpha=1) # set scale and ordinates values
		# plt.xticks(scale, aminoAcid)  # do not show ticks
		plt.ylabel('Intensity')
		plt.xlabel('Residue number')
		axes = plt.gca()
		axes.xaxis.set_tick_params(labelsize = 5)
		plt.title('Intensities at step '+str(listNumber))
	
	plt.show()




