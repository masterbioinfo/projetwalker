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

Authors : Hermès PARAQUINDES, Louis Duchemin, Marc-Antoine GUENY and Rainier-Numa GEORGES for Dr. Olivier WALKER and Dr. Maggy HOLOGNE 
(ISA-UMR 5280 CNRS,5 Rue de la DOUA, 69100 Villeurbanne -FRANCE). 
This program is developped in Python 3.5.1, Anaconda v5.0.0, JuPyter v5.2.0, MatPlotLib v2.1.0, 
on Ubuntu v16.04.3 LTS (UNIX core system). 
Date of creation : 2017-10-13.
Last modification : 2017-10-24.

Exemple :  ./index.py data/listes/listPP/*.list"""


import functions
import os
import sys
from docopt import docopt
import classes.AminoAcid as aa
from classes.Titration import Titration
from matplotlib import pyplot as plt

args = docopt(__doc__)

#Enter experimentals files :
if args["<file.list>"]:
	titration = Titration(args["<file.list>"])
elif args["<dir>"]:
	titration = Titration(args["<dir>"])

titration.plotHistogram()
titration.plotHistogram(1)
titration.plotChemShifts(titration.complete[0:10],split=True)
titration.plotChemShifts(split=False)
#Cutoff selection by the user.
plt.ion()
oldCutoff = 0
newCutoff = float(input("select cut off :\n"))
titration.plotHistogram(cutOff=newCutoff)
newCutoff = float(input("select cut off :\n"))
exit(1)
#newCutoff = functions.cutoffSelection()

#Plot(s) selection by the user.
#plotSelected = functions.plotSelection(deltaDeltaShifts)

#functions.setHistogram(validatedResidues,None, (newCutoff))

###Operating phase:
print("\nWelcolme to Shift2Me - The only dating site for proteins !!!")

##Initialization session parameters:
#The program continues to work while "quit" = False.
quit = False
#All commands support by the program, the number before call the same commands than the string indicate after : number_command(i), command(i).
order = ["1", "2Dmap", "2", "cutoff", "3", "", "help", "4", "histogram", "5", "load", "6", "quit", "7", "save", "8", "select residu"]
#If we don't load a file who contains an older job, listResidu select all AminoAcid object by default:
#Else listResidu is load from the file who contains the older job.
if directoryIn["extensionIn"] == "list":
	residuSelected = listResidus


while quit == False:
	
	#Select a command by is number or is proper name.
	selectOrder = list(" ")
	while selectOrder[0] not in order:
		selectOrder[0] = input("\nPlease, enter a command. (default: 'help')\n")
		selectOrder = str (selectOrder[0])
		selectOrder.lower()
		selectOrder = selectOrder.split(" ")

		if selectOrder[0] in order:
			pass
		else :
			print('This is not valid order. Please refere to "help" section to see all valids commands.')
					
	if selectOrder[0] == "2Dmap" or selectOrder == "1" :
		#Show 2Dmap.
		pass

	elif selectOrder[0] == "cutoff" or selectOrder == "2" :
		#The user selction a residu.
		if len(selectOrder) == 1 :
			functions.showCutoff(plotsAndCutoffs)
		elif len(selectOrder) == 3 :
			newCutoff = functions.cutoffSelection(plotsAndCutoffs, selectOrder)
			#Plot(s) selectionned by the user and affiliate cutoff selectionned with plot selectionned.
			plotsAndCutoffs = functions.plotSelection(plotsAndCutoffs, newCutoff, selectOrder)
		else :
			print('With command "cutoff", tou must indicate the new cutoff and a plot affected by cutoff ("all" for all plots). (ex: "cutoff 0.5 4")!')
	
	elif selectOrder[0] == "help" or selectOrder == "" or selectOrder == "3" :
		#Help commands.
		functions.helpOrder()

	elif selectOrder[0] == "histogram" or selectOrder == "4" :
		#Show histograms.
		#graphic = functions.histograms(deltaDeltaShifts, plotsAndCutoffs)
		#print(graphic)
		pass

	elif selectOrder[0] == "load" or selectOrder == "5" :
		#Load older job.
		(listFileTitration, plotsAndCutoffs, listResidus, loadMessage) = functions.loadAsk()
		print(loadMessage)

	elif selectOrder[0] == "quit" or selectOrder == "6" :
		#Quit the program and save the current job.
		quit = functions.quitProgram()
		datasToBeSave = (listFileTitration, plotsAndCutoffs, listResidus, residuSelected)
		saveCurrentJob = functions.saveAsk(directoryIn, datasToBeSave)

	elif selectOrder[0] == "save" or selectOrder == "7":
		#Save the current job.
		datasToBeSave = (listFileTitration, plotsAndCutoffs, listResidus, residuSelected)
		saveCurrentJob = functions.saveAsk(directoryIn, datasToBeSave)

	elif selectOrder[0] == "select residu" or selectOrder == "8" :
		#Select a residu to explore him. All residus can be selected too.
		residuSelected = functions.residuSelection(listResidus)


###Goodbye message.
print("\n\nSee you soon on Sheeft2Me !!! ;-)")


