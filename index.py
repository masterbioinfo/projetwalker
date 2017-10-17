#!/usr/bin/python3
# -*- encoding: utf-8 -*-
"""	
Shift2Me Project - Dating site for proteins !!!

Usage: index.py <file.list> <file.list> ... [ -o <output_dir> ]

Options:
	-o <output_dir>, --output-dir <output_dir>  Output generated files to <output_dir>.

This program can calculate chimicals shifts of 15N and 1H during a portein protein interaction in fonction of titation of the secondary protein. 
He generate plots to show chemicals shifts for each titration of the secondary protein. You can fix a cutoff to appreciate residus involved in protein protein interaction. 
You can see all chemical shift of interest 2D maps (N15/1H) too.

Authors : Hermès PARAQUINDES, Louis Duchemin, Marc-Antoine GUENY, Rainier-Numa GEORGES, Dr. Olivier WALKER, Dr. Maggy HOLOGNE (ISA-UMR 5280 CNRS,5 Rue de la DOUA, 69100 Villeurbanne -FRANCE). 
This program is developped in Python 3.5.1, date of creation : 2017-10-13, last modification : 2017-10-16.
"""	

"""
Exemple :  ./index.py data/listes/listPP/*.list
"""

import methods
import os
import sys
from docopt import docopt
import classes.AminoAcid as aa



args = docopt(__doc__)

#Enter experimentals files :
listFileTitration = args["<file.list>"]

#Validate file path and sort them
sortedPath = methods.sortPath(listFileTitration)

# build AminoAcid object dictionnary
residues = dict()
for titrationFile in listFileTitration :
	residues = methods.parseTitrationFile(titrationFile, residues)

validatedResidues = [ residue for residue in residues.values() if residue.validate(len(sortedPath)) ]
incompleteDataResidues = [residue for residue in residues.values() if not residue.validate(len(sortedPath))]
print(validatedResidues)
print(incompleteDataResidues)
print(len(residues))
"""
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

"""
