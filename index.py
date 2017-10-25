#!/usr/bin/python3
# -*- encoding: utf-8 -*-
"""	
Shift2Me Project - Dating site for proteins !!!

Usage: 
	index.py <file.list> <file.list> ... [ -o <output_dir> ]
	index.py <dir>

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
from classes.Titration import Titration

args = docopt(__doc__)

#Enter experimentals files :
if args["<file.list>"]:
	titration = Titration(args["<file.list>"])
elif args["<dir>"]:
	titration = Titration(args["<dir>"])


titration.plotChemShifts(titration.complete[0:10],split=True)
titration.plotChemShifts(split=False)
titration.plotHistogram(6)

#Cutoff selection by the user.
oldCutoff = 0
newCutoff = functions.cutoffSelection()
titration.plotHistogram(cutOff=newCutoff)
titration.plotHistogram(6,cutOff=newCutoff)

titration.extractResidues(cutOff = 0, targetFile = 'okok.txt')

#Plot(s) selection by the user.
#plotSelected = functions.plotSelection(deltaDeltaShifts)

#functions.setHistogram(validatedResidues,None, (newCutoff))



