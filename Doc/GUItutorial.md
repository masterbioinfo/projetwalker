
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

3. [About](#about)


Shift2Me :sparkles: : 2D-NMR chemical shifts analyzer for protein protein interactions (PPI).
===============================

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
You need to install jupyter notebook and specific widgets to use graphical mode of ShiftoMe.

1. To install jupyter notebook, run the command :
```
pip3 install jupyter
```
See [jupyter documentation](http://jupyter.readthedocs.io/en/latest/install.html) for installation.

2. To clone Shift2Me via gitHub and install its dependancies, run the following commands :
```
git clone https://github.com/masterbioinfo/projetwalker.git
pip3 install -r requirements.txt
```
A repository _projetwalker_ which contains ShifttoMe is created.

3. To activate jupyter widgets, run the commands :
```
jupyter nbextension enable --py widgetsnbextension

jupyter nbextension enable --py --sys-prefix ipyfileupload

jupyter nbextension enable --py --sys-prefix bqplot
```

## 2-Launch Shift2Me <a name="launch"></a>:
Reach the directory in which the file _GUI.ipynb_ is located and run the command :
```
jupyter notebook
```

Access to the file _GUI.ipynb_. Your are now in the __GUI__ interface of ShiftoMe.

See [jupyter documentation](http://jupyter-notebook.readthedocs.io/en/stable/examples/Notebook/Notebook%20Basics.html) for notebook usage.

## 3-Upload your files <a name="upload"></a>:

1. Click on **Upload titration directory** to upload all the .list files provided by your NMR titration. You must choose a directory in which all the .list files will be loaded.

Your files appear in the window:

|Data files|
|------|
|15N_UIM-SH3-37_00.list |
|15N_UIM-SH3-37_01.list |
|15N_UIM-SH3-37_02.list |
|15N_UIM-SH3-37_03.list |
|15N_UIM-SH3-37_04.list |
|15N_UIM-SH3-37_05.list |
|15N_UIM-SH3-37_06.list |
|15N_UIM-SH3-37_07.list |
|15N_UIM-SH3-37_08.list |
|15N_UIM-SH3-37_09.list |
|15N_UIM-SH3-37_10.list |

2. The second cell outputs a protocol titration.

You should fill and submit the protocol settings to have access to all plots available. **Analyte** fields refer to the protein you add step by step, **Titrant** fields refer to the protein whose quantity is constant along NMR titration.
- _Name_ fields will set the name of your titration, analyte or titrant.
- _Concentration_ fields assign **initial concentrations** of the proteins in µM.
- _Analyte volume_ and _Total volume_ refer to the volumes in µL added at step 0 of titration (without titrant). _Total volume_ includes **proteic volumes and solvant**.

Click on **Validate** once you completed the fields.

## 5-Histogram
Below the protocol, a data vizualisation containing the graphs will appear. The first graph displayed is the histogram.
On the left of the graph, are situated two sliders with which the user can interact. The first one allows the user to choose a titration step. The second one, to set a new cutoff. Intensities bigger than the cutoff are colored in orange, the rest is colored in blue. Only the intensities bigger than the cutoff are retained by the filter.

## 8-Exit Shift2Me <a name="exit"></a>:
This is the essential part of Shift2Me. Those graphic representations will help you to define a suitable cutoff filtering residues implicated in PPI and thus determine affinnity parameters.


# About <a name="about"></a> :
---
This program is developped by :

- **_Louis DUCHEMIN_**
- **_Marc-Antoine GUERY_**
- **_Hermes PARAQINDES_**
- **_Rainer-Numa GEORGES_**

	students in [**Master 1 Molecular Bio-Informatic**](https://www.bioinfo-lyon.fr/) of [**Claude Bernard Lyon 1 University (UCBL)**](https://www.univ-lyon1.fr/), mandated by **_Maggy HOLOGNE and Olivier WALKER_** **PhDs** of [**Institut des Sciences Analytiques (ISA, CNRS - UMR 5280)**](https://isa-lyon.fr/).

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
