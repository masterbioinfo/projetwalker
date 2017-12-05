#!/usr/bin/python3
# -*- encoding: utf-8 -*-
"""
Shift2Me : 2D-NMR chemical shifts analysis for protein interactions.

Usage:
    shift2me.py [-c <cutoff>] [-i <titration.json>] [-t <file.json>] [<file.list> <file.list> ...]
    shift2me.py [-c <cutoff>] [-i <titration.json>] [-t <file.json>] ( <dir> | <saved_job> )
    shift2me.py -h

Options:
  -c <cutoff>, --cut-off=<cutoff>                       Set default cutoff at <cutoff> (float).
  -i <titration.json>, --init-file=<titration.json>     Initialize titration from file.json (JSON format)
  -t <file.json>, --template=<file.json>                Initialize a template titration.json file,
                                                        to be filled with titration parameters.
  -h --help                                             Print help and usage

This program can calculate chemicals shifts of 15N and 1H during a portein protein interaction in fonction of titation of the secondary protein.
He generate plots to show chemicals shifts for each titration of the secondary protein. You can fix a cutoff to appreciate residus involved in protein protein interaction.
You can see all chemical shift of interest 2D maps (N15/1H) too.

Example :  ./shift2me.py data/listes/listPP/*.list

Authors : Hermès PARAQUINDES, Louis Duchemin, Marc-Antoine GUERY and Rainier-Numa GEORGES
"""

from docopt import docopt
from matplotlib import pyplot as plt
from classes.Titration import BaseTitration, Titration
from classes.command import ShiftShell


if __name__ == '__main__':
    args = docopt(__doc__)
    #print(args)


    source = args["<file.list>"] or args["<dir>"]
    titration = Titration(source, cutoff=args["--cut-off"], initFile=args['--init-file'])

    # Build titration instance
    if args["--template"]:
        template = args["--template"]
        templateBuilder = titration if titration.isInit else BaseTitration()
        templateBuilder.dump_init_file(initFile = template)
        print("Generated template file at {file}".format(file=template))
        exit()

    # Turn off MPL interactive mode
    plt.ioff()
    # Init CLI
    cli = ShiftShell(titration = titration)
    # Start main loop
    cli.cmdloop()
