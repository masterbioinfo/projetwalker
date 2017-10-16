"""Module functions, classes and methods use during Shift2Me works.

Developped by Hermès PARAQUINDES, Louis Duchemin, Marc-Antoine GUENY ans Rainier-Numa GEORGES for Dr. Olivier WALKER and Dr. Maggy HOLOGNE (ISA-UMR 5280 CNRS,5 Rue de la DOUA, 69100 Villeurbanne -FRANCE). This program is developped in Python 3.5.1, date of creation : 2017-10-13, last modification : 2017-10-13.
"""

from math import *

###############################################################################################


					### Functions ###


###############################################################################################

"""All functions used during process are wrote here."""


def informationsFile(listFileTitration):

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
				

def parseTitrationFile(titrationFile, listChemicalShift, residusForgetted, directoryIn, missingDatas, residusNotRetained):

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
					for titration in residusNotRetained :
						for residue in titration :
							#If the residu, who don't have all chemicals shifts, is already write in residusNotRetained list, we don't write him in the list.
							if residue == chemicalShift[0] :
								pass
							#The residu isn't in residusNotRetained list, so we take him to work on him.
							else :
								chemicalShiftAssignements["residue"] = chemicalShift[0]
								chemicalShiftAssignements["chemicalShiftN"] = chemicalShift[4]
								chemicalShiftAssignements["chemicalShiftH"] = chemicalShift[10]
								listChemicalShiftParsed.append(chemicalShiftAssignements)
				#If other line, not planned in the file, are presents the program print a message error.
				else :
					raise ValueError ("A line in {0} isn't in support format (.list).".format(titrationFile))

		listChemicalShift.append(listChemicalShiftParsed)
		f.close()
		return listChemicalShift
			
	except IOError:
		print("File doesn't exists !")


def calculateRelativesShifts(listChemicalShift):

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
	
	newCutoff = input("What cutoff value do you want applied ?\n")
	
	try :
		newCutoff = float(newCutoff)
		if newCutoff <= 10 and newCutoff >= 0:
			print("New cutoff applied = {0}.".format(newCutoff))
			return newCutoff
		else:
			if newCutoff > 10 :
				raise ValueError ("Cutoff selected is too higher! It's must be lower or equal than 10 !") 
			elif newCutoff < 0 :
				raise ValueError ("Cutoff selected is too lower! It's must be higher or equal than 0 !") 
	except TypeError:
		if plotSelected != float :
			print("Cutoff value must be integer or decimal !")


def plotSelection():

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
