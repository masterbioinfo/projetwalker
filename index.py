#!/usr/bin/python3

# -*- encoding: utf-8 -*-

"""Shift2Me Project - Dating site for proteins !!!

This program can calculate chimicals shifts of 15N and 1H during a portein protein interaction in fonction of titation of the secondary protein. 
He generate plots to show chemicals shifts for each titration of the secondary protein. 
You can fix a cutoff to appreciate residus involved in protein protein interaction. 
You can see all chemical shift of interest 2D maps (N15/1H) too.

Authors : Hermès PARAQUINDES, Louis Duchemin, Marc-Antoine GUENY and Rainier-Numa GEORGES for Dr. Olivier WALKER and Dr. Maggy HOLOGNE 
(ISA-UMR 5280 CNRS,5 Rue de la DOUA, 69100 Villeurbanne -FRANCE). 
This program is developped in Python 3.5.1, Anaconda v5.0.0, JuPyter v5.2.0, MatPlotLib v2.1.0, 
on Ubuntu v16.04.3 LTS (UNIX core system). 
Date of creation : 2017-10-13.
Last modification : 2017-10-24.

Usage: index.py <file.list> <file.list> ...

Exemple :  ./index.py data/listes/listPP/*.list"""


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


###Load .list files, parse files, extract datas, create AminoAcid objects and compute values:
if directoryIn["extensionIn"] == "list" and len(listFileTitration) >= 1:
	try:
		###Test of all files format at ".list" extension:
		goodFormats = functions.formatVerification(listFileTitration)


		###Creation of file who takes only residus not retained in the study because all chemicals shifts aren't presents.
		residusForgetted = "{0}residus_not_retained.txt".format(directoryIn["pathIn"])
		writeResidusNotRetained = open(residusForgetted, "w", encoding = "utf-8")	
		writeResidusNotRetained.close()


		###Parsed each files to retained all residus without all chemicals shifts in a other file and in a list of residus not retained.
		residusNotRetained = list()
		listChemicalShift = list()
		missingDatas = True
		for titrationFile in listFileTitration :
			residusNotRetained = functions.parseTitrationFile(titrationFile, listChemicalShift, residusForgetted, missingDatas, residusNotRetained)
	

		###Parsed each files to retained all residus with all chemicals shifts in a list of residus retained.
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


		###For each residus retained, intensity of chemical shift relative is calculate.
		for residu in listResidus:
			residu.chemShiftIntensity

		###List of dictionnaries is creat to contains plots numbers and cutoffs at format : plot: n, cutoff: c.
		plotsAndCutoffs = list()
		i = 0
		while i < len(listResidus[52].chemShiftIntensity) :
			plotCutoffs = {"plot" : i, "cutoff" : None}
			plotsAndCutoffs.append(plotCutoffs)
			i += 1
	except IOError as err:
		sys.stderr.write("%s\n" % err)
		exit(1)


###Load file who contains the last job (pkl):
elif directoryIn["extensionIn"] == "txt" and len(listFileTitration) == 2 :
	try :
		###Load the last job automatically. The file loaded must be write in CLI.
		(listFileTitration, plotsAndCutoffs, listResidus, loadMessage) = functions.loadJob(directoryIn)
		print(loadMessage)
	except IOError as err:
			sys.stderr.write("%s\n" % err)
			exit(1)


###Operating phase:
print("\nWelcolme to Shift2Me - The only dating site for proteins !!!")

##Initialization session parameters:
#The program continues to work while "quit" = False.
quit = False
#All commands support by the program, the number before call the same commands than the string indicate after : number_command(i), command(i).
order = ["1", "2Dmap", "2", "cutoff", "3", "", "help", "4", "histogram", "5", "load", "6", "quit", "7", "save", "8", "select_residu"]
#If we don't load a file who contains an older job, listResidu select all AminoAcid object by default:
#Else listResidu is load from the file who contains the older job.
if directoryIn["extensionIn"] == "list":
	residuSelected = listResidus


while quit == False:
	
	selectOrder = functions.orderSelected(order)
	quit = functions.controls(selectOrder, quit, directoryIn, listFileTitration, plotsAndCutoffs, listResidus, residuSelected)

###Goodbye message.
print("\n\nSee you soon on Sheeft2Me !!! ;-)")

