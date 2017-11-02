#!/usr/bin/python3
# -*- encoding: utf-8 -*-
"""	
Shift2Me Project - Dating site for proteins !!!

Usage: 
	index.py <file.list> <file.list> ... [ -o <output_dir> ]
	index.py <dir>

Options:
	-o <output_dir>, --output-dir <output_dir>  Output generated files to <output_dir>.

This program can calculate chemicals shifts of 15N and 1H during a portein protein interaction in fonction of titation of the secondary protein. 
He generate plots to show chemicals shifts for each titration of the secondary protein. You can fix a cutoff to appreciate residus involved in protein protein interaction. 
You can see all chemical shift of interest 2D maps (N15/1H) too.

Authors : Hermès PARAQUINDES, Louis Duchemin, Marc-Antoine GUENY and Rainier-Numa GEORGES for Dr. Olivier WALKER and Dr. Maggy HOLOGNE 
(ISA-UMR 5280 CNRS,5 Rue de la DOUA, 69100 Villeurbanne -FRANCE). 
This program is developped in Python 3.5.1, Anaconda v5.0.0, JuPyter v5.2.0, MatPlotLib v2.1.0, 
on Ubuntu v16.04.3 LTS (UNIX core system). 
Date of creation : 2017-10-13.
Last modification : 2017-10-24.

Exemple :  ./index.py data/listes/listPP/*.list
"""

from docopt import docopt
from matplotlib import pyplot as plt
from classes.Titration import Titration
from classes.command import ShiftShell


args = docopt(__doc__)

#Enter experimentals files :
if args["<file.list>"]:
	titration = Titration(args["<file.list>"])
elif args["<dir>"]:
	titration = Titration(args["<dir>"])

#Cutoff selection by the user.
plt.ion()
cli = ShiftShell(titration = titration)
cli.cmdloop()
