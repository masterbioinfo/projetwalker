
# Table of contents
----
1. [Summary](#summary)
2. [Tutoriel](#tutoriel)

	2.1. [Introduction](#introduction)

    2.2. [Launch Shift2Me](#launch)

    2.3. [Basics commands](#basics_commands)

    2.4. [Initiating your protocol titration](#init)

    2.5. [Filter and select residues](#filter_select)

    2.6. [2D shift map, histograms and titration curve](#graphs)

    2.7. [Save and load](#save_load)

    2.8. [Exit Shift2Me](#exit)


3. [Commands](#commands)


Shift2Me :sparkles: : 2D-NMR chemical shifts analyzer for protein protein interactions (PPI).
===============================
---

This program is developped by **_Louis DUCHEMIN, Hermes PARAQINDES, Marc-Antoine GUERY and Rainier-Numa GEORGES_**, students in **Master 1 Molecular Bio-Informatic** of **Claude Bernard Lyon 1 University (UCBL)**, mandated by **_Maggy HOLOGNE and Olivier WALKER_** **PhDs** of **Institut des Sciences Analytiques (ISA, CNRS - UMR 5280)**.

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

# Summary <a name="summary"></a>:

------------------------------------------
Shift2me is a 2D-NMR chemical shifts analyzer for PPI. The goal of the program is to identify the residues implicated in a PPI.

Given a .list file format, which contains the Residues numbers and the chemical shifts of ^15^N and ^1^H, the program will calculate the delta of the chemical shifts for each titration done during the experience.

Different graphs will be generated at the end.

- __A map2D__ : Two-dimensional graph wich shows the evolution of the chemicals shifts of ^15^N and ^1^H during each titration for all the residues.

- __Histogram__ : A histogram for each titration will show the delta of the chemical shifts in function of the residue number. In order to select the residues implicated in a PPI, the user can choose a cutoff.

- __Curves__ : A curve can be generated for each residue implicated in a PPI. The curve shows the delta of the chemical shifts of the residue in fuction of the the ratio of the concentration of the titrant protein to the concentration of the titrated protein.
- In __GUI__ mode, a representation 3D of the protein structure is added. The user can choose a PDB code, the residues numbers and change the representation mode.


------------------------------------------

# Tutorial <a name="tutoriel"></a>:

------------------------------------------

## 1-Introduction <a name="introduction"></a> :

Shift2Me use a shell terminal like Linux. You can use autocompletion with TAB touch. For exemple, to write the "select" command you can write "sel" then push TAB touch to do autocompletion of "sel" in "select". You have access to shortcuts:

	* ! *: shell
	* ? *: help
	* @ *: load
	* @@ *: relative load

## 2	-Launch Shift2Me <a name="launch"></a>:
At the first place, you must provide to Shift2Me a list of files including NMR experiment datas.

1. To launch Shift2Me, you should indicate a data directory path. If the directory includes the data issued from the NMR experiment, the program will analyze it automatically. All the titration steps added after the program is launched will be saved in the directory indicated at launch. For example : if the directory path is "data/listes/listPP/", you can launch the program using the command:
```
python3 shift2me.py data/listes/listPP
```
To add one or more .list file stored in the repository _data/listupdated_ after the program is launched, use the command :
```
update data/listupdated
```
2. If any data were included in the directory indicated, the program will list a summary:
```

	* Source dir 		-> the data path
	* Steps				-> the number of steps experiments
	* Cutoff			-> cutoff selected
	* Total residues	-> Total residues in the study
		- Complete residues 	-> Total residues in the study
 		- Incomplete residues	-> Number of residues with incomplete informations (not retained in the study)
 		- Filtered residues		-> Number of residus filtered (0 in the first time)
```
All this information is accessible with the command :
```
summary
```

## 3-Basics commands <a name="basics_commands"></a> :

1. You have access at any time to help section of Shift2Me. To show all the commands available, you can enter :
```
help
```
Or :
```
?
```

You can show help information for one specific command. Example :
```
help summary
```
2. To see all the commands entered during the current job use the command:
```
history
```
3. You have also the possibility to set the titration name by using the command :
```
set_name
```
To name your work _Ubiquitin titration_, use:
```
set_name "Ubiquitin Titration"
```

## 4-Initiating your protocol titration <a name="init"></a>:
You should fill and submit a protocol file so you will have access to all plots available.
1. You can indicate all titrations parameters in a .yml file. To create a .yml file that contains these parameters use the command :
```
dump_protocole <file_name>
```
After creating the .yml file, open the file using a text editor inside the shell terminal of Shift2Me. Example :
```
!nano <file_name.yml>
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

Shift2Me will perform data analysis even without completing the protocole file (.yml), but it can not generate the curve graphs for the filtered residues.

3. The program gives the possibility to add volumes of each titration step with the command :
```
add_volumes
```
Example, after loading a .list file, you can indicate the titrant protein volume added for the current titration step :
```
add_volumes 2.5
```
You can also idicate successive volumes added.
If the number of steps added is 3 then you can use the command :
```
add_volumes 2.5 3 3.5
```
4. Finally **set_volumes** command can be used to replace a volume if a mistake has been made.
For example, if your current set of volumes is  _3 3.5 4_, then replace it entering :
```
set_volumes 3 4 5
```
## 5-Filter and select residues <a name="filter_select"></a> :
You can select relevant residues in order to show them on the different graphic representations available (see next section).
1. To set or modify the cutoff value of your job, use the command :
```
cutoff
```
For example, if you want to apply an intensity threshold of 0.2, type :
```
cutoff 0.2
```
2. You can filter all the residues that have an equal or higher cutoff than the one indicated :
```
filter
```
3. To select specific residues either from a predefined set of residues or from one or more slices of residue positions, you can use :
```
select
```
Predefined sets of residues are : all, filtered, complete, incomplete. For example, to select filtered residues :
```
select filtered
```
You can also select specific residues. For example, to match residues _105_ and _112_ to _115_ (excluded) :
```
select 105 112:115
```
You may mix argument types, like select filtered residues and residues _100_ to _110_ (excluded) :
```
select filtered 100:110
```
Notice that non existant residues are skipped with a warning message.
Finally, selection is additive only, each selected element adds up to previous selection.
If you want to clear the current selection, use **deselect** command (see next section).

3. You can deselect residues using **deselect** command, which works the same way as the **select** command.
For example,  if you selected residues _218_, _221_ and _224_ and you just need residues _218_ and _224_, enter:
```
deselect 221
```

4. You can show filtered, complete, incomplete or selected residues using the command :
```
residues
```
For example, to show selected residues :
```
residues selected
```

## 6-2D shift map, histograms and titration curve <a name="graphs"></a>:
This is the essential part of Shift2Me. Those graphic representations will help you to define a suitable cutoff filtering residues implicated in PPI and thus determine affinnity parameters.

1. You can display the whole 2D shift map with (x= ^1^H ppm, y= ^15^N ppm)by entering **shiftmap** command. This graphs shows the evolution of the chemicals shifts of ^15^N and ^1^H (in ppm) during each titration step for all the residues. Chemicals shifts are modeled on the graph with differents colors (one color per titration step). Residues sets availabale are complete, filtered and selected residues.
For example, to show selected residues shiftmap, use:
```
shiftmap selected
```
Invocation with no arguments of this command will plot all residues with complete data.
To show a splitted shiftmap of filtered residues, use:
```
shiftmap -s filtered
```

3. To help the user to determinate the residues implicated in a PPI, use the command **hist** to plot chemical shift intensity per residu as histograms.
To display all histograms of chemicals shifts, for all steps and all residues retained in the study, enter :
```
hist all
```
Or:
```
hist 0
```
If you want to display only one histogram for one step (for exemple the fifth step), enter:
```
hist 5
```
To show the histogram of the last step, enter:
```
hist
```
You can interact with the histograms by using the mouse. You can select a new cutoff with one drag and drop of the mouse. Chemical shifts bigger than the cutoff are colored in orange, others chemicals shifts are colored in blue. Only chemicals shifts bigger than the cutoff are retained by the filter. This cutoff will be saved as the new cutoff of your job.

3. To display titration curve, enter **curve** command follow by a residue number.The curve shows the intensity of the chemical shifts of the residue in fuction of the the ratio of the concentration (in µM) of the titrant protein to the concentration (in µM) of the titrated protein.
```
Example : Curve 218
```
## 7-Save and load <a name="save_load"></a>:
Before leaving Shift2Me, you should save the state of your job or you history commands.
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
```
```
load_job data/listes/listPP/save.pkl
```


2. You can load a list of history commands written in _history0911.txt_ with **load** command.
```
load history0911.txt
```

## 8-Exit Shift2Me <a name="exit"></a>:

1. To quit Shift2Me, enter "quit" command. You will go back to the bash shell of Linux.
```
quit
```
------------------------------------------

# Commands <a name="commands"></a>:

------------------------------------------
To see the full list of commands with their description, please refer to the documentation file.
