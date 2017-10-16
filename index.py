"""	Shift2Me Project - Dating site for proteins !!!

	This program can calculate chimicals shifts of 15N and 1H during a portein protein interaction in fonction of titation of the secondary protein. 
	He generate plots to show chemicals shifts for each titration of the secondary protein. You can fix a cutoff to appreciate residus involved in protein protein interaction. 
	You can see all chemical shift of interest 2D maps (N15/1H) too.
	
	Developped by Hermès PARAQUINDES, Louis Duchemin, Marc-Antoine GUENY ans Rainier-Numa GEORGES for Dr. Olivier WALKER and Dr. Maggy HOLOGNE (ISA-UMR 5280 CNRS,5 Rue de la DOUA, 69100 Villeurbanne -FRANCE). This program is developped in Python 3.5.1, date of creation : 2017-10-13, last modification : 2017-10-13.
	"""	

#!/usr/bin/python
# -*- encoding: utf-8 -*-



import methods
import os
import sys



titrationFile_0 = "data/listes/listPP/15N_UIM-SH3-37_00.list"
titrationFile_1 = "data/listes/listPP/15N_UIM-SH3-37_01.list"
#titrationFile_2 = "data/listes/listPP/15N_UIM-SH3-37_02.list"
#titrationFile_3 = "data/listes/listPP/15N_UIM-SH3-37_03.list"
#titrationFile_4 = "data/listes/listPP/15N_UIM-SH3-37_04.list"
#titrationFile_5 = "data/listes/listPP/15N_UIM-SH3-37_05.list"
#titrationFile_6 = "data/listes/listPP/15N_UIM-SH3-37_06.list"
#titrationFile_7 = "data/listes/listPP/15N_UIM-SH3-37_07.list"
#titrationFile_8 = "data/listes/listPP/15N_UIM-SH3-37_08.list"
#titrationFile_9 = "data/listes/listPP/15N_UIM-SH3-37_09.list"
#titrationFile_10 = "data/listes/listPP/15N_UIM-SH3-37_10.list"

listFileTitration = [titrationFile_0, titrationFile_1]

#listFileTitration = [titrationFile_0, titrationFile_1, titrationFile_2, titrationFile_3, titrationFile_4, titrationFile_5, titrationFile_6, titrationFile_7,titrationFile_8, titrationFile_9, titrationFile_10]


directoryIn = methods.informationsFile(listFileTitration)


goodFormats = methods.formatVerification(listFileTitration)


#Creation of file who takes only residus not retained in the study because all chemical shift aren't presents.
residusForgetted = "{0}residus_not_retained.txt".format(directoryIn["pathIn"])
writeResidusNotRetained = open(residusForgetted, "w", encoding = "utf-8")	
writeResidusNotRetained.close()


residusNotRetained = list()
listChemicalShift = list()
#Search all residus without all chemicals shifts.
missingDatas = True
for titrationFile in listFileTitration :
	residusNotRetained = methods.parseTitrationFile(titrationFile, listChemicalShift, residusForgetted, directoryIn, missingDatas, residusNotRetained)

#Search then takes all residus with xho have all chemicals shifts in listChemicalShift.
listChemicalShift = list()
missingDatas = False	
for titrationFile in listFileTitration :
	listChemicalShift = methods.parseTitrationFile(titrationFile, listChemicalShift, residusForgetted, directoryIn, missingDatas, residusNotRetained)


listChemicalShift = methods.calculateRelativesShifts(listChemicalShift)
print(listChemicalShift)

deltaDeltaShifts = list()
deltaDeltaShifts = methods.deltaDeltaChemicalsShifts(listChemicalShift)	


oldCutoff = 0
newCutoff = methods.cutoffSelection()
plotSelected = methods.plotSelection()

