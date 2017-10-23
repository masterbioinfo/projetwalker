# -*- encoding: utf-8 -*-
"""
Module functions, classes and methods use during Shift2Me works.

Authors : Hermès PARAQUINDES, Louis Duchemin, Marc-Antoine GUENY and Rainier-Numa GEORGES for Dr. Olivier WALKER and Dr. Maggy HOLOGNE (ISA-UMR 5280 CNRS,5 Rue de la DOUA, 69100 Villeurbanne -FRANCE). This program is developped in Python 3.5.1, date of creation : 2017-10-13, last modification : 2017-10-16.
"""



###############################################################################################


					### Moduls ###


###############################################################################################

#Moduls used in methods.py.


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


def informationsFile(listFileTitration):
	"""The fonction takes the all path of the file. Then she return the path without the file's name (pathIn), 
	the file's name(fileNameOpen), the file's extension (extensionIn) in the dictionary named "directory". 
	Also, she test if the file name is ".list" or "exlist". If it's not the case, she return an error."""

	try:
		for fileInformations in listFileTitration:
			directory = {"pathIn" : None, "fileNameOpen": None, "extensionIn": None}
			fileInformations = fileInformations.split(".")
			directory["extensionIn"] = fileInformations[1]	
		
			#If open file have ".list" extension :
			if directory["extensionIn"] == "list" or directory["extensionIn"] == "exlist" :	
				fileInformations = str(fileInformations[0]).split("/")
				directory["fileNameOpen"] = fileInformations[-1]
				i = 0
				path = ""
			
				#Reformating open file's path :
				while i < len(fileInformations) - 1 :
					path = path + "{0}/".format(fileInformations[i])
					i += 1 
				directory["pathIn"] = path
			
			#If open file haven't ".list" extension :
			else :
				raise IOError("Le fichier {0} n'a pas d'extension '.list'".format(fileInformation))

		return directory
	except IOError as err:
		sys.stderr.write("%s\n" % err)
		exit(1)

def formatVerification(listFileTitration):
	"""The fonction takes the list who contained all files's paths. She test all files. If a file ".list" is in the good format,
	she return True. In other case, she return an error with the file's name. To do that, the file tested must be open, his first 
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

def parseTitrationFile(titrationFile, listChemicalShift, residusForgetted, missingDatas, residusNotRetained):
	"""This function takes in arguments: the file's path (titrationFile), the list who will contains all chemicals 
		shifts after parsing(listChemicalShift), the path of the file who contains all residu not retained in the study,
		the variable missingDatas, and the list of all residus not retained in the study because they don't
		have all chemicals shifts (residusNotRetained).

	In a first time, the file past in argument, is open and parsed line after line.
	In a second time, if missingDatas = True, so we search all resdus without all chemicals shifts (one missing). If the line
		tested reveals one chemical shift is missing, then this residus is write in the not retained residus's file and
		in residusNotRetained list. In the other case, nothing his write and we pass to next line of the file parsed.
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
					#Line in the headers don't retained.
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
						raise ValueError ("A line in {0} isn't in support format (.list).".format(titrationFile))

		listChemicalShift.append(listChemicalShiftParsed)

		return listChemicalShift
			
	except IOError as err:
		sys.stderr.write("%s\n" % err)
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
		if newCutoff <= 2 and newCutoff >= 0:
			print("New cutoff applied = {0}.".format(newCutoff))
			return newCutoff
		else:
			if newCutoff > 2 :
				raise ValueError ("Cutoff selected is too higher! It's must be lower or equal than 5 !") 
			elif newCutoff < 0 :
				raise ValueError ("Cutoff selected is too lower! It's must be higher or equal than 0 !") 
	except TypeError:
		if plotSelected != float :
			print("Cutoff value must be integer or decimal !")


def plotSelection(plotsAndCutoffs, newCutoff):
	"""This function takes plotsAndCutoffs list in argument, she return the selected plot (type : int).The user 
	can choose the selected plot. Then the function return plotsAndCutoffs list with a the affiliation between
	plot(s) selectionned and cutoff selectionned previously.
	If the plot is in 0 and the plotsAndCutoffs list length, the function return the selected plot. 
	If the value entry isn't in acceptables values, the function return an error. If the value cannot 
	be transform in integer type, the function return an error. 
	They are an exception if the user write "all", or "All", or "ALL", in this case, the user
	selected all plots."""
	
	plotSelected = input('Which plot do you want to select ? [default : all] \n')

	try :
		if plotSelected:
			plotSelected = int(plotSelected)
	
			if plotSelected  <= len(plotsAndCutoffs) and plotSelected  >= 0:
				plotsAndCutoffs[plotSelected]["cutoff"] = newCutoff
				print("You have selectionned plot n°{0}.".format(plotSelected))
				return plotsAndCutoffs
			else:
				if plotSelected > len(plotsAndCutoffs) :
					raise ValueError ("The plot choose cannot be selected !") 
				elif plotSelected < 0 :
					raise ValueError ("Plots numbers cannot be inderior of 0 !") 
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
	except ValueError:
		if plotSelected != "all":
			print('Enter "all" to selection all plots.')

def jsonSaveJob(directoryIn, listFileTitration, plotsAndCutoffs, deltaDeltaShifts):
	"""This function takes directoryIn and plotsAndCutoffs dictionnaries, plus listFileTitration
	and deltaDeltaShifts lists. She allow to save listeFileTitration, plotsAndCutoffs and delatDeltaShifts
	at json format. She return a confirmation message. In the other case, she return a message error."""

	try:
		datasSave = [listFileTitration, plotsAndCutoffs, deltaDeltaShifts]
		with open("{0}saveJob.json".format(directoryIn["pathIn"]), 'w') as saveJobFile:
			saveJobFile.write(json.dumps(datasSave, indent=5))
		return "Job saves in {0}saveJob.json !".format(directoryIn["pathIn"])
	except IOError as err:
		sys.stderr.write("%s\n" % err)
		exit(1)


def jsonLoadJob(directoryIn):
	"""This function takes directoryIn dictionnay in argument and return datasLoad list who contains
	all element saved in the save file at json format : listeFileTitration, plotsAndCutoffs, 
	deltaDeltaShifts. Plus, the function return a confirmation message.
	In the other case, she return a message error."""

	try:
		with open("{0}saveJob.json".format(directoryIn["pathIn"]), 'r') as loadJobFile:
			datasLoad = json.load(loadJobFile) 
		loadMessage = "Job loads from {0}saveJob.json !".format(directoryIn["pathIn"])
		datasLoad.append(loadMessage)
		return datasLoad
	except IOError as err:
		sys.stderr.write("%s\n" % err)
		exit(1)

def jsonSaveJob(directoryIn, listFileTitration, plotsAndCutoffs, deltaDeltaShifts):
    """ """
    try:
        datas = [listFileTitration, plotsAndCutoffs, deltaDeltaShifts]
        with open("{0}saveJob.json".format(directoryIn["pathIn"]), 'w') as saveJobFile:
            saveJobFile.write(json.dumps(datas, indent = 5)) 
        return "Job saves in {0}saveJob.exlist !".format(directoryIn["pathIn"]) 
    except IOError as err:
        sys.stderr.write("%s\n" % err)
        exit(1)


def jsonLoadJob(directoryIn):
    """ """
    
    liste = list()
    try:
        with open("{0}saveJob.json".format(directoryIn["pathIn"]), 'r') as loadJobFile:
            datas = json.load(loadJobFile)
        return "Job saves in {0}saveJob.exlist !".format(directoryIn["pathIn"]) 
    except IOError as err:
        sys.stderr.write("%s\n" % err)
        exit(1)


def saveJob(directoryIn, listFileTitration, plotsAndCutoffs, listResidus):
	"""The function can save the job. She takes diretoryIn dictionnary, listFileTitration list, 
	plotsAndCutoffs list and deltaDeltaShifts list in arguments. She return a confirmation message.
	If save cannot save objects in the file, she return an error message."""
	
	try:
		with open("{0}saveJob.list".format(directoryIn["pathIn"]), 'ab') as saveJobFile:
			my_pickler = pickle.Pickler(saveJobFile)
			my_pickler.dump(listFileTitration)
			my_pickler.dump(plotsAndCutoffs)
			my_pickler.dump(listResidus)
	        
		return "Job saves in {0}saveJob.list !".format(directoryIn["pathIn"])
	except IOError as err:
		sys.stderr.write("%s\n" % err)
		exit(1)
	


def loadJob(directoryIn):
	"""The function can load the last job save. She takes directoryIn dictionnary in argument. She
	return elemntsLoads list. This list contains objects loaded from the save file: listFileTitration 
	list, plotsAndCutoffs list and deltaDeltaShifts list."""
	
	elementsLoads = list()

	try :	
		with open("{0}saveJob.list".format(directoryIn["pathIn"]), 'rb') as loadJobFile:
			my_depickler = pickle.Unpickler(loadJobFile)

			listFileTitration = my_depickler.load()
			elementsLoads.append(listFileTitration)

			plotsAndCutoffs = my_depickler.load()
			elementsLoads.append(plotsAndCutoffs)

			listResidus = my_depickler.load()
			elementsLoads.append(listResidus)

		loadMessage = "Job loads from {0}saveJob.list !".format(directoryIn["pathIn"])
		elementsLoads.append(loadMessage)
		return elementsLoads
	except IOError as err:
		sys.stderr.write("%s\n" % err)
		exit(1)
	

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




