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

Authors : Hermès PARAQUINDES, Louis Duchemin, Marc-Antoine GUENY, Rainier-Numa GEORGES, Dr. Olivier WALKER, Dr. Maggy HOLOGNE. 
"""	

"""
Exemple :  ./index.py data/listes/listPP/*.list
"""


import functions
import os
import sys
from docopt import docopt
import classes.AminoAcid as aa

args = docopt(__doc__)

#Enter experimentals files :
listFileTitration = args["<file.list>"]

#Validate file path and sort them
sortedPath = functions.sortPath(listFileTitration)

# build AminoAcid object dictionnary
residues = dict()
for titrationFile in listFileTitration :
	residues = functions.parseTitrationFile(titrationFile, residues)

validatedResidues = [ residue for residue in residues.values() if residue.validate(len(sortedPath)) ]
incompleteDataResidues = [residue for residue in residues.values() if not residue.validate(len(sortedPath))]
print (validatedResidues[3].chemShiftIntensity)

# After parsing : 
# residues is dict with all AminoAcid
# validatedResidues is dict with AminoAcid having complete data
# incompleteDataResidues : residues with missing data


#Cutoff selection by the user.
oldCutoff = 0
newCutoff = functions.cutoffSelection()


#Plot(s) selection by the user.
#plotSelected = functions.plotSelection(deltaDeltaShifts)

functions.setHistogram(validatedResidues,None, (newCutoff))



