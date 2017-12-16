Shift2Me :sparkles: : 2D-NMR chemical shifts analyzer for protein protein interactions (PPI).
===============================


This program is developped by **_Louis DUCHEMIN, Hermes PARAQINDES, Marc-Antoin GUERY and Rainier-Numa GEORGES_**, students in **Master 1 Molecular Bio-Informatic** of **Claude Barnard Lyon 1 University (UCBL)**, mandated by **_Maggy HOLOGNE and Olivier WALKER_** **PhDs** of **Institut des Sciences Analytiques (ISA, CNRS - UMR 5280)**.

```
Institut des Sciences Analytiques
CNRS - UMR 5280
5 Rue de la DOUA
69100 Villeurbanne - FRANCE
```
```
Université Claude Bernard Lyon 1
43 Boulevard du 11 Novembre 1918
69100 Villeurbanne - FRANCE
```
------------------------------------------

# Summary:

------------------------------------------
Shift2me is a 2D-NMR chemical shifts analyzer for PPI. The goal of the program is to identify the residues implicated in a PPI.

Given a .list file format, which contains the Residues numbers and the chemical shifts of 15N and 1H, the program will calculate the delta of the chemical shifts for each titration done during the experience.

Different graphs will be generated at the end.

- __A map2D__ : Two-dimensional graph wich shows the evolution of the chemicals shifts of 15N and 1H during each titration for all the residues.

- __Histogram__ : A histogram for each titration will show the delta of the chemical shifts in function of the residue number. In order to select the residues implicated in a PPI, the user can choose a cutoff.

- __Curves__ : A curve can be generated for each residue implicated in a PPI. The curve shows the delta of the chemical shifts of the residue in fuction of the the ratio of the concentration of the titrant protein to the concentration of the titrated protein.
- In __GUI__ mode, a representation 3D of the protein structure is added. The user can choose a PDB code, the residues numbers and change the representation mode.


------------------------------------------

# Tutorial:

------------------------------------------

## Introduction:

Shift2Me use a shell terminal like Linux. You can use autocompletion with TAB touch. For exemple, to write the "select" command you can write "sel" then push TAB touch to do autocompletion of "sel" in "select". You have access to shortcuts:

	* ! *: shell
	* ? *: help
	* @ *: load
	* @@ *: relative load

If you want use shortcuts to load files, you must write the file path after the shortcut. For exemple :

	@  data/listes/listPP/data/listes/listPP/15N_UIM-SH3-37_01.list

## 1-Launch Shift2Me :

1. To launch Shift2Me, you should indicate a data directory path. If the directory includes the data issued from the NMR experience, the program it will analyse automatically. If not, all the titration step added after the program is launched, will be saved in the directory indicated. For example : if the directory path is "data/listes/listPP/", you can launch the program using the command:
```
	python3 shift2me.py data/listes/listPP
```
2. If any data were included in the directery indicated, the program will list a summary:
```

	* Source dir 		-> the data path
	* Steps				-> the number of steps experiments
	* Cutoff			-> cutoff selected
	* Total residues	-> Total residues in the study
		- Complete residues 	-> Total residues in the study
 		- Incomplete residues	-> Number of residues with incomplete informations (not retained in the study)
 		- Filtered residues		-> Number of residus filtered (0 in the first time)
```
All the information is accessible with the command :
```
summary
```

## 2-Basics commands :

1. You have access at any time to help section of Shift2Me. To show all the commands diponible, you can enter:
```
help or ?
```

You can show help information for one specific command. Example:
```
help summary
```
2. To see all the commands entered during the current job use the command:
```
history
```

## 3-Concentrations and volumes :

1. The user has the possibility to indicate all titrations parameters in a .yml file. To create a .yml file that contains these parameters use the command :
```
dump_protocole <file_name>
```
After creating the .yml file, open the file using a text editor inside the shell terminal of Shift2Me. Example :
```
!nano <file_name.yml
```
The .yml file contains all the information above:
```
_description: This file defines a titration's initial parameters.
name: Unnamed Titration
analyte:
    concentration: 0
    name: analyte
titrant:
    concentration: 0
    name: titrant
start_volume:
    analyte: 0
    total: 0
add_volumes: []
```
Notice that all volumes are in **µL** and concentrations are in **µM**.

Shift2Me will analyze the data even without completing the protocole file (.yml), but it can not generate the curves graphs for the filtred residues.

The program gives the possibility to add volumes of each titration step with the command:
```
add_volumes
```
Example, after loading a .list file, you can indicate the volume of the titrant protein added for the titration step:
```
add_volumes 2.5
```
You can also idicate the volumes added after loading all data obtained.
If the number of steps added is 3 then you can use the command :
```
set_volumes 2.5 3 3.5
```
The same command can be used to replace a volume if a mistake has been made.
```
Old set of volumes :  3 3.5 4

To replace : set_volumes 3 4 5
```
The user has also the possibility to set the titration name by using the command :
```
set_name
Example : set_name "Ubiquitin Titration"
```

## 4-Select and Filter residues :

1. To select specific residues you can use :
```
select
Select a subset of residues, either from :
         - a predefined set of residues
         - 1 or more slices of residue positions, with python-ish syntax.
        Examples :
            ':100' matches positions from start to 100
            '110:117' matches positions from 100 to 117 (excluded)
            '105 112:115' matches positions 105 and 112 to 115 (excluded)
        You may mix argument types, like select filtered residues + res #100 to #110 excluded :
            >> select filtered 100:110
        Non existant residues are skipped with a warning message.
        Finally, selection is additive only, each selected element adds up to previous selection.
        If you want to clear the current selection, use deselect command.

Usage: select [all] [filtered] [complete] [incomplete] [positions_slice]
```

2. You can deselect residues using **deselect** command, which works the same way as the **select** command
```
deselect

Usage: deselect arg
```

3. To filter residues with a high chemical shift, use the command :
```
cutoff
Usage: cutoff [options] <float>
Example : cutoff 0.2
```
4. You can filter all the residues that have an equal or higher cutoff than the one indicated
```
filter
```
5. To show filtered, selected, complete or incomplete residues use :
```
residues
Usage: residues ( filtered | selected | complete | incomplete )
```


## 5-Titration curve, 2D shift map and histograms :

1. To diplay titration curve, enter **curve** command follow by a residue number.The curve shows the intensity of the chemical shifts of the residue in fuction of the the ratio of the concentration (in µM) of the titrant protein to the concentration (in µM) of the titrated protein.
```
Example : Curve 218
```

2. You can display the whole 2D shift map with (x= 1H ppm, y= 15N ppm)by entering **shiftmap** command. This graphs shows the evolution of the chemicals shifts of 15N and 1H (in ppm) during each titration step for all the residues. Chemicals shifts are modeled on the graph with differents colors (one color per titration step).

```
shiftmap

Usage: shiftmap [options] ( complete | filtered | selected )
```
Invocation with no arguments of this command will plot all residues with complete data.

3. To help the user to determinate the residues implicated in a PPI, use the command **hist** to plot chemical shift intensity per residu as histograms.
```
hist

Usage: hist [options] (<titration_step> | all)

```
To display all histograms of chemicals shifts, for all steps and all residues retained in the study, enter :
```
hist all or hist 0
```
If you want to display only one histogram for one step (for exemple the fifth step), enter:
```
hist 5
```
To show the histogram of the last step, enter:
```
hist
```
You can interact with the histograms by using the mouse. You can select a new cutoff with one drag and drop of the mouse. Chemical shifts bigger than the cutoff are colored in orange, others chemicals shifts are colored in blue. Only chemicals shifts bigger than the cutoff are retained by the filter.

You can select a new cutoff by only using the Shift2Me shell terminal.

## 6-Save and load:

1. At any time you can save your current job with **save_job** command.
 ```
 save_job
```
This command saves your current job in a binary file. This gives the possibility to just load the saved job in the Shift2Me terminal. To do so use the command **load_job**.
```
load_job
```
Example of use :
```
save_job data/listes/listPP/save
load_job data/listes/listPP/save.pkl
```


2. You can load a new experimental file during a job with **load** command.
```
load
```

Loading a file allows to display on standard output the whole data contents in the file too.
	* load data/listes/listPP/15N_UIM-SH3-37_12.list *

Once done, you can reselect cutoff, residues etc.

## 7-Exit Shift2Me:

1. To quit Shift2Me, enter "quit" command. You will go back to the bash shell of Linux.
```
quit
```
------------------------------------------

# Commands:

------------------------------------------
To see the full list of commands with their description, please refer to the documentation file.
