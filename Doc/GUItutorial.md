
# Table of contents
----
1. [Summary](#summary)
2. [Tutorial](#tutorial)

	2.1. [Installation](#installation)

    2.2. [Launch Shift2Me](#launch)

    2.3. [Upload](#upload)

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

- In __GUI__ mode, a representation 3D of the protein structure is added. The user can choose a PDB code, the residues numbers and change the representation mode (soon available).


------------------------------------------

# Tutorial <a name="tutorial"></a>:

------------------------------------------

## 1-Installation <a name="installation"></a> :
First of all, ensure you have a python 3 (or more) version. To check your version, enter in the terminal shell :
```
pip -V python
```
You need to install jupyter and specific widgets to use __GUI__ mode od ShiftoMe.

1. To install jupyter notebook, run the command :
``` 
pip3 install jupyter
```
See [jupyter documentation](http://jupyter.readthedocs.io/en/latest/install.html) for installation.

2. To install and activate ipywidgets, ipyfileupload and bqplot, run the commands :
``` 
pip3 install ipywidgets
jupyter nbextension enable --py widgetsnbextension
```
```
pip3 ipyfileupload
jupyter nbextension enable --py --sys-prefix ipyfileupload
```
```
pip3 bqplot
jupyter nbextension enable --py --sys-prefix bqplot
```

3.Finally you need all the requirements we mentionned for our __CLI__ version of ShiftoMe

## 2-Launch Shift2Me <a name="launch"></a>:
Reach the directory in which the file _GUI.ipynb_ is located and run the command :
```
jupyter notebook
```

Access to the file _GUI.ipynb_. Your are now in the __GUI__ interface of ShiftoMe.

See [jupyter documentation](http://jupyter-notebook.readthedocs.io/en/stable/examples/Notebook/Notebook%20Basics.html) for notebook usage.

## 3-Upload your files <a name="upload"></a>:
Run the first cell of __GUI__ ShifttoMe. Select **Upload titration directory** to upload all the files provided by your NMR titration.

Your files apper in the window:

Data files|
---|---
15N_UIM-SH3-37_00.list |
15N_UIM-SH3-37_01.list |
15N_UIM-SH3-37_02.list |
15N_UIM-SH3-37_03.list |
15N_UIM-SH3-37_04.list |
15N_UIM-SH3-37_05.list |
15N_UIM-SH3-37_06.list |
15N_UIM-SH3-37_07.list |
15N_UIM-SH3-37_08.list |
15N_UIM-SH3-37_09.list |
15N_UIM-SH3-37_10.list |


## 4-Initiating your protocol titration <a name="init"></a>:
You should fill and submit a protocol file so you will have access to all plots available.

Run the second cell of __GUI__ Shitf2Me.

Select **Validate** once you completed the fields.


## 8-Exit Shift2Me <a name="exit"></a>:
This is the essential part of Shift2Me. Those graphic representations will help you to define a suitable cutoff filtering residues implicated in PPI and thus determine affinnity parameters.
