#!/usr/bin/python3
# -*- encoding: utf-8 -*-

"""Shift2Me Project - Dating site for proteins !!!

This program can calculate chimicals shifts of 15N and 1H during a portein protein interaction in fonction of titation of the secondary protein. 
He generate plots to show chemicals shifts for each titration of the secondary protein. 
You can fix a cutoff to appreciate residus involved in protein protein interaction. 
You can see all chemical shift of interest 2D maps (N15/1H) too.

Authors : Hermès PARAQUINDES, Louis Duchemin, Marc-Antoine GUENY and Rainier-Numa GEORGES for Dr. Olivier WALKER and Dr. Maggy HOLOGNE 
(ISA-UMR 5280 CNRS,5 Rue de la DOUA, 69100 Villeurbanne -FRANCE). 
This program is developped in Python 3.5.1 on Ubuntu v16.04.3 LTS (UNIX core system). 
Date of creation : 2017-10-13.
Last modification : 2017-10-24.

Usage: index.py <file.list> <file.list> ...

Exemple :  ./index.py data/listes/listPP/*.list
"""


###############################################################################################


					### Moduls ###


###############################################################################################

#Moduls used in Shift2Me.py.


from classes.AminoAcid import AminoAcid
from math import *
import functions
import os
import sys
from docopt import docopt


###############################################################################################


					### Main ###


###############################################################################################


###Enter experimentals files :
args = docopt(__doc__)
listFileTitration = args["<file.list>"]


###Test of all extensions files : 
directoryIn = functions.informationsFile(listFileTitration)


###Load .list files, parse files and extract datas:
if directoryIn["extensionIn"] == "list" and len(listFileTitration) >= 1:
	try:
		###Test of all files format:
		goodFormats = functions.formatVerification(listFileTitration)


		###Creation of file who takes only residus not retained in the study because all chemical shift aren't presents.
		residusForgetted = "{0}residus_not_retained.txt".format(directoryIn["pathIn"])
		writeResidusNotRetained = open(residusForgetted, "w", encoding = "utf-8")	
		writeResidusNotRetained.close()


		###Parsed each files to retained all residus without all chemicals shifts in a file and in a list.
		residusNotRetained = list()
		listChemicalShift = list()
		missingDatas = True
		for titrationFile in listFileTitration :
			residusNotRetained = functions.parseTitrationFile(titrationFile, listChemicalShift, residusForgetted, missingDatas, residusNotRetained)
	

		###Parsed each files to retained all residus with all chemicals shifts in a list.
		listChemicalShift = list()
		missingDatas = False	
		for titrationFile in listFileTitration :
			listChemicalShift = functions.parseTitrationFile(titrationFile, listChemicalShift, residusForgetted, missingDatas, residusNotRetained)


		#Objects residus initialisation.
		listResidus = functions.aminoAcideObjectsCreation(listChemicalShift)


		###For each residus retained, each chemicals shifts are calculate in a relative form.
		for residu in listResidus:
			residu.deltaChemShiftH
			residu.deltaChemShiftN


		###For each residus retained, delta(ChemicalShift) is calculate.
		for residu in listResidus:
			residu.chemShiftIntensity

		###List of dictionnaries creation who contains plots numbers and cutoffs at format : plot: n, cutoff: c.
		plotsAndCutoffs = list()
		i = 0
		while i < len(listResidus[52].chemShiftIntensity) :
			plotCutoffs = {"plot" : i, "cutoff" : None}
			plotsAndCutoffs.append(plotCutoffs)
			i += 1
	except IOError as err:
		sys.stderr.write("%s\n" % err)
		exit(1)


###Load files who contains the last job:
elif directoryIn["extensionIn"] == "txt" and len(listFileTitration) == 2 :
	try :
		###Load job in progress automatically. The file loaded must be write in CLI.
		(listFileTitration, plotsAndCutoffs, listResidus, loadMessage) = functions.loadJob(directoryIn)
		#(listFileTitration, plotsAndCutoffs, listResidus, loadMessage) = functions.jsonLoadJob(directoryIn)
		print(loadMessage)
	except IOError as err:
			sys.stderr.write("%s\n" % err)
			exit(1)


###Operating phase:
quit = False
while quit == False:
	
	###Cutoff selection by the user.
	newCutoff = functions.cutoffSelection()


	###Plot(s) selectionned by the user and affiliate cutoff selectionned with plot selestionned.
	plotsAndCutoffs = functions.plotSelection(plotsAndCutoffs, newCutoff)


	###Show histograms.
	#graphic = functions.histograms(deltaDeltaShifts, plotsAndCutoffs)
	#print(graphic)
	
	quitMessage = None
	while quitMessage != "yes" and quitMessage != "no": 
		quitMessage = input("Do you want quit this program ? (yes/no)")
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

	saveJobAsk = None
	while saveJobAsk != "yes" and saveJobAsk != "no":
		saveJobAsk = input("Do you want save your job ? (yes/no)")
		try:
			saveJobAsk = str(saveJobAsk)
			saveJobAsk.lower()
			
			if saveJobAsk == "yes":
				###Save job in progress automatically.
				saveMessage = functions.saveJob(directoryIn, listFileTitration, plotsAndCutoffs, listResidus)
				#saveMessage = functions.jsonSaveJob(directoryIn, listFileTitration, plotsAndCutoffs, listResidus)
				print(saveMessage)
			elif saveJobAsk == "no" :
				print("The current job don't be save.")
			else :
				raise ValueError
		except ValueError:
			print('Please, would you indicate if you want save your current job ("yes") or not ("no").')
			saveJobAsk = None

print("See you soon on Sheeft2Me !!! ;-)")

