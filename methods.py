# -*- encoding: utf-8 -*-
"""
Module functions, classes and methods use during Shift2Me works.

Authors : Hermès PARAQUINDES, Louis Duchemin, Marc-Antoine GUENY and Rainier-Numa GEORGES for Dr. Olivier WALKER and Dr. Maggy HOLOGNE (ISA-UMR 5280 CNRS,5 Rue de la DOUA, 69100 Villeurbanne -FRANCE). This program is developped in Python 3.5.1, date of creation : 2017-10-13, last modification : 2017-10-16.
"""



###############################################################################################


					### Moduls ###


###############################################################################################

#Moduls used in methods.py.


from math import *
import matplotlib.pyplot as plt
import numpy as num


###############################################################################################


					### Functions ###


###############################################################################################

#All functions used during process are wrote here.


def informationsFile(listFileTitration):
	"""The fonction takes the all path of the file. Then she return the path without the file's name (pathIn), 
	the file's name(fileNameOpen), the file's extension (extensionIn) in the dictionary named "directory". 
	Also, she test if the file name is ".list". If it's not the case, she return an error."""

	for fileInformations in listFileTitration:
		directory = {"pathIn" : None, "fileNameOpen": None, "extensionIn": None}
		fileInformations = fileInformations.split(".")
		directory["extensionIn"] = fileInformations[1]	
		
		#If open file have ".list" extension :
		if directory["extensionIn"] == "list" :	
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

def formatVerification(listFileTitration):
	"""The fonction takes the list who contained all files's paths. She test all files. If a file ".list" is in the good format,
	she return True. In other case, she return an error with the file's name. To do that, the file tested must be open, his first 
	three lines are parsed and then tested on seven marks."""

	for titrationFile in listFileTitration :
		testFileArray = list()			#Takes the first three lines of each file to test if the file have a good format.
		f = open(titrationFile, "r", encoding = "utf-8")
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
		#Else, the function declare the file is not with the good format and raise an error :
		else:
			raise IOError ('Le fichier {0} n\'est pas enregistré au foramt ".list".'.format(titrationFile))

		f.close()
				

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
		f = open(titrationFile, "r", encoding = "utf-8")

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
				if chemicalShift[0] != "Assignment" and chemicalShift[0] != "" and (chemicalShift[4] == "" or len(chemicalShift) < 10) :
						listChemicalShiftParsed.append(chemicalShift[0])
						aaNotRetained = "{0}\t{1}\n".format(titrationFile, chemicalShift[0]) 
						fileAaNotRetained = open(residusForgetted, "a")
						fileAaNotRetained.write(aaNotRetained + "\n")
						fileAaNotRetained.close()

			#In a second time, we don't search residu without all chemicals shifts, we search residus with all informations.
			elif missingDatas == False :
				#Line in the headers don't retained.
				if chemicalShift[0] == "Assignment" or chemicalShift[0] == "" :
					pass
				#Residus without all chemicals shifts are not retained.
				elif chemicalShift[4] == "" or len(chemicalShift) < 10 :
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
		f.close()
		return listChemicalShift
			
	except IOError:
		print("File doesn't exists !")


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




