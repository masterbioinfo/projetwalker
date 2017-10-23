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


from classes.AminoAcid import AminoAcid
from math import *
import functions
import os
import sys
from docopt import docopt


###Enter experimentals files :

args = docopt(__doc__)

listFileTitration = args["<file.list>"]


###Test of all extensions files : 
directoryIn = functions.informationsFile(listFileTitration)


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
listResidus = list()
for chemicalShift in listChemicalShift[0]:
	residu = AminoAcid(**chemicalShift)
	listResidus.append(residu)
#Add chemShiftH and chemShiftN for each residu.
i = 1 
while i < len(listChemicalShift):
	j = 0
	while j < len(listChemicalShift[i]):
		listResidus[j].chemShiftH.append(float(listChemicalShift[i][j]["chemicalShiftH"]))
		listResidus[j].chemShiftN.append(float(listChemicalShift[i][j]["chemicalShiftN"]))
		j += 1
	i += 1

###For each residus retained, each chemicals shifts are calculate in a relative form.
#listChemicalShift = functions.calculateRelativesShifts(listChemicalShift)
for residu in listResidus:
	residu.deltaChemShiftH
	residu.deltaChemShiftN


###For each residus retained, delta(ChemicalShift) is calculate.
#deltaDeltaShifts = list()
#deltaDeltaShifts = functions.deltaDeltaChemicalsShifts(listChemicalShift)
for residu in listResidus:
	residu.chemShiftIntensity


###List of dictionnaries creation who contains plots numbers and cutoffs at format : plot: n, cutoff: c.
plotsAndCutoffs = list()

i = 0
while i < len(listResidus[0].chemShiftIntensity) :
	plotCutoffs = {"plot" : i, "cutoff" : None}
	plotsAndCutoffs.append(plotCutoffs)
	i += 1
print(plotsAndCutoffs)


###Cutoff selection by the user.
newCutoff = functions.cutoffSelection()


###Plot(s) selectionned by the user and affiliate cutoff selectionned with plot selestionned.
plotsAndCutoffs = functions.plotSelection(plotsAndCutoffs, newCutoff)


###Save job in progress automatically.
saveMessage = functions.saveJob(directoryIn, listFileTitration, plotsAndCutoffs, listResidus)
#saveMessage = functions.jsonSaveJob(directoryIn, listFileTitration, plotsAndCutoffs, listResidus)
print(saveMessage)


###Load job in progress automatically. The file loaded must be write in CLI.
#fileLoad = args["<file.list>"]
#directoryIn = functions.informationsFile(fileLoad)
(listFileTitration, plotsAndCutoffs, listResidus, loadMessage) = functions.loadJob(directoryIn)
#(listFileTitration, plotsAndCutoffs, listResidus, loadMessage) = functions.jsonLoadJob(directoryIn)
print(loadMessage)


###Show histograms.
#graphic = functions.histograms(deltaDeltaShifts, plotsAndCutoffs)
#print(graphic)

