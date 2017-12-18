#!/usr/bin/python3
# -*- encoding: utf-8 -*-
"""
Shift2Me : 2D-NMR chemical shifts analysis for protein interactions.

Usage:
    shift2me.py [-c <cutoff>] [-i <titration.yml>] [-t <file.yml>] ( <dir> | <saved_job> )
    shift2me.py -h

Options:
  -c <cutoff>, --cut-off=<cutoff>                       Set default cutoff at <cutoff> (float).
  -i <titration.yml>, --init-file=<titration.yml>     Initialize titration from file.yml (YML format)
  -t <file.yml>, --template=<file.yml>                Initialize a template titration.yml file,
                                                        to be filled with titration parameters.
  -h --help                                             Print help and usage

ShiftoMe enables you to determine which residues are significantly implicated in a protein-protein interaction.
The program is based on calculation of intensities from 15N and 1H chemical shifts measured during a protein-protein 
interaction in a NMR titration experiment.
It helps you to identify relevant residues to study thanks to splittable 2D shiftmaps and interactive step-by-step 
intensity per residue histograms.

Example :  ./shift2me.py data/listes/listPP

Authors : Hermes PARAQINDES, Louis Duchemin, Marc-Antoine GUERY and Rainier-Numa GEORGES
"""

from docopt import docopt
from matplotlib import pyplot as plt
from classes.Titration import BaseTitration, TitrationCLI
from classes.command import ShiftShell


if __name__ == '__main__':
    ARGS = docopt(__doc__)

    TITRATION_KWARGS = {
        "working_directory":ARGS["<dir>"],
        "cutoff": ARGS["--cut-off"] or 0.1,
        "initFile": ARGS['--init-file']
    }

    titration = TitrationCLI(**TITRATION_KWARGS)

    # Build titration instance
    if ARGS["--template"]:
        template = ARGS["--template"]
        templateBuilder = titration if titration.isInit else BaseTitration()
        templateBuilder.dump_init_file(initFile = template)
        print("Generated template file at {file}".format(file=template))

    # Turn off MPL interactive mode
    plt.ioff()
    # Init CLI
    CLI = ShiftShell(titration = titration)
    # Start main loop
    CLI.cmdloop()
