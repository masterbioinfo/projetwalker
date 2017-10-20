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


###Enter experimentals files :

args = docopt(__doc__)

listFileTitration = args["<file.list>"]


###Test of all extensions files : 
directoryIn = methods.informationsFile(listFileTitration)


###Test of all files format:
goodFormats = methods.formatVerification(listFileTitration)


###Creation of file who takes only residus not retained in the study because all chemical shift aren't presents.
residusForgetted = "{0}residus_not_retained.exlist".format(directoryIn["pathIn"])
writeResidusNotRetained = open(residusForgetted, "w", encoding = "utf-8")	
writeResidusNotRetained.close()


###Parsed each files to retained all residus without all chemicals shifts in a file and in a list.
residusNotRetained = list()
listChemicalShift = list()
missingDatas = True
for titrationFile in listFileTitration :
	residusNotRetained = methods.parseTitrationFile(titrationFile, listChemicalShift, residusForgetted, missingDatas, residusNotRetained)
	print(residusNotRetained)


###Parsed each files to retained all residus with all chemicals shifts in a list.
listChemicalShift = list()
missingDatas = False	
for titrationFile in listFileTitration :
	listChemicalShift = methods.parseTitrationFile(titrationFile, listChemicalShift, residusForgetted, missingDatas, residusNotRetained)
print(listChemicalShift)


###For each residus retained, each chemicals shifts are calculate in a relative form.
listChemicalShift = methods.calculateRelativesShifts(listChemicalShift)


###For each residus retained, delta(ChemicalShift) is calculate.
deltaDeltaShifts = list()
deltaDeltaShifts = methods.deltaDeltaChemicalsShifts(listChemicalShift)	


###List of dictionnaries creation who contains plots numbers and cutoffs at format : plot: n, cutoff: c.
plotsAndCutoffs = list()

i = 0
while i < len(deltaDeltaShifts) :
	plotCutoffs = {"plot" : i, "cutoff" : None}
	plotsAndCutoffs.append(plotCutoffs)
	i += 1
print(plotsAndCutoffs)


###Cutoff selection by the user.
newCutoff = methods.cutoffSelection()


###Plot(s) selectionned by the user and affiliate cutoff selectionned with plot selestionned.
plotsAndCutoffs = methods.plotSelection(plotsAndCutoffs, newCutoff)


###Save job in progress automatically.
#saveMessage = methods.saveJob(directoryIn, listFileTitration, plotsAndCutoffs, deltaDeltaShifts)
saveMessage = methods.jsonSaveJob(directoryIn, listFileTitration, plotsAndCutoffs, deltaDeltaShifts)
print(saveMessage)


###Load job in progress automatically. The file loaded must be write in CLI.
#fileLoad = args["<file.list>"]
#directoryIn = methods.informationsFile(listFileTitration)
#(listFileTitration, plotsAndCutoffs, deltaDeltaShifts, loadMessage) = methods.loadJob(directoryIn)
(listFileTitration, plotsAndCutoffs, deltaDeltaShifts, loadMessage) = methods.jsonLoadJob(directoryIn)
#print(loadMessage)


###Show histograms.
#graphic = methods.histograms(deltaDeltaShifts, plotsAndCutoffs)
#print(graphic)

