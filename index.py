#!/usr/bin/python3
# -*- encoding: utf-8 -*-
"""	
Shift2Me Project - Dating site for proteins !!!

This program can calculate chimicals shifts of 15N and 1H during a portein protein interaction in fonction of titation of the secondary protein. 
He generate plots to show chemicals shifts for each titration of the secondary protein. You can fix a cutoff to appreciate residus involved in protein protein interaction. 
You can see all chemical shift of interest 2D maps (N15/1H) too.

Authors : Hermès PARAQUINDES, Louis Duchemin, Marc-Antoine GUENY, Rainier-Numa GEORGES, Dr. Olivier WALKER, Dr. Maggy HOLOGNE (ISA-UMR 5280 CNRS,5 Rue de la DOUA, 69100 Villeurbanne -FRANCE). 
This program is developped in Python 3.5.1, date of creation : 2017-10-13, last modification : 2017-10-16.

Usage: index.py <file.list> <file.list> ...
"""	

"""
Exemple :  ./index.py data/listes/listPP/*.list
"""

import methods
import os
import sys
from docopt import docopt


#Enter experimentals files :

args = docopt(__doc__)

listFileTitration = args["<file.list>"]

#Test of all extensions files : 
directoryIn = methods.informationsFile(listFileTitration)


#Test of all files format:
goodFormats = methods.formatVerification(listFileTitration)


#Creation of file who takes only residus not retained in the study because all chemical shift aren't presents.
residusForgetted = "{0}residus_not_retained.txt".format(directoryIn["pathIn"])
writeResidusNotRetained = open(residusForgetted, "w", encoding = "utf-8")	
writeResidusNotRetained.close()


#Parsed each files to retained all residus without all chemicals shifts in a file and in a list.
residusNotRetained = list()
listChemicalShift = list()
missingDatas = True
for titrationFile in listFileTitration :
	residusNotRetained = methods.parseTitrationFile(titrationFile, listChemicalShift, residusForgetted, missingDatas, residusNotRetained)
	print(residusNotRetained)


#Parsed each files to retained all residus with all chemicals shifts in a list.
listChemicalShift = list()
missingDatas = False	
for titrationFile in listFileTitration :
	listChemicalShift = methods.parseTitrationFile(titrationFile, listChemicalShift, residusForgetted, missingDatas, residusNotRetained)
print(listChemicalShift)


#For each residus retained, each chemicals shifts are calculate in a relative form.
listChemicalShift = methods.calculateRelativesShifts(listChemicalShift)


#For each residus retained, delta(ChemicalShift) is calculate.
deltaDeltaShifts = list()
deltaDeltaShifts = methods.deltaDeltaChemicalsShifts(listChemicalShift)	

#Cutoff selection by the user.
oldCutoff = 0
newCutoff = methods.cutoffSelection()


#Plot(s) selection by the user.
plotSelected = methods.plotSelection(deltaDeltaShifts)

graphic = methods.graph (deltaDeltaShifts)
print (graphic)

