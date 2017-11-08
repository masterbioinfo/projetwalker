# -*- encoding: utf-8 -*-

"""
Module classes uses during Shift2Me works.

Authors : Hermès PARAQUINDES, Louis Duchemin, Marc-Antoine GUENY and Rainier-Numa GEORGES for Dr. Olivier WALKER and Dr. Maggy HOLOGNE 
(ISA-UMR 5280 CNRS,5 Rue de la DOUA, 69100 Villeurbanne -FRANCE). 
This program is developped in Python 3.5.1, Anaconda v5.0.0, JuPyter v5.2.0, MatPlotLib v2.1.0, 
on Ubuntu v16.04.3 LTS (UNIX core system).
Date of creation : 2017-10-13
Last modification : 2017-10-24.
"""

###############################################################################################


                    ### Moduls ###


###############################################################################################

#Moduls used in AminoAcid.py.


import math, sys


###############################################################################################


                    ### Classes ###


###############################################################################################


class AminoAcid(object):
    """
    Class AminoAcid
    Describes a amino-acid using its position number in the proteic sequence.
    An AminoAcid object contains the values of measured chemical shift at each titration step. 
    These data are split in two lists, one contains the hydrogen chem shift data, the other contains nitrogen chem shifts data.
    The first element of each list is used as a reference value for calculating difference in chemical shifts at each titration step, i.e measured chem shift - ref chem shift. 
    """

    def __init__(self, **kwargs):
        """
        Initialize AminoAcid object, only required argument is position.
        If chemshiftH and chemshiftN are provided, use them to start both chemical shift lists.
        """
        self.position = int(kwargs["position"])
        self.chemshiftH = [float(kwargs["chemshiftH"])] if kwargs.get("chemshiftH") else []
        self.chemshiftN = [float(kwargs["chemshiftN"])] if kwargs.get("chemshiftN") else []
        self._deltaChemshiftH = None
        self._deltaChemshiftN = None
        self._chemshiftIntensity = None
    def __str__(self):
        return str((self.position, self.chemshiftH, self.chemshiftN))

    def __repr__(self):
        return self.__str__()

    def add_chemshift(self, **kwargs):
        """
        Append chemical shifts to object's lists of chemical shifts
        If one of the values is missing, None or 0, it is ignored.
        """
        if kwargs.get("chemshiftH") and float(kwargs["chemshiftH"]) != 0:
            self.chemshiftH.append(float(kwargs["chemshiftH"]))
        if kwargs.get("chemshiftN") and float(kwargs["chemshiftN"]) != 0:
            self.chemshiftN.append(float(kwargs["chemshiftN"]))

    def validate(self, titrationSteps):
        """
        Checks wether an AminoAcid object contains all chemical shift data (1 for each titration step)
        """
        return True if len(self.chemshiftH) == len(self.chemshiftN) == titrationSteps else False

    @property
    def deltaChemshiftH(self):
        """
        Calculates distance to the reference for each chemical shift only once for hydrogen.
        """
        try :
            self._deltaChemshiftH = tuple([dH - self.chemshiftH[0] for dH in self.chemshiftH[1:]])
            return self._deltaChemshiftH
        except IndexError as missingDataError:
            sys.stderr.write("Could not calculate chem shift variation for residue %s : missing H chem shift data" % self.position)
            exit(1)


    @property
    def deltaChemshiftN(self):
        """
        Calculates distance to the reference for each chemical shift only once for nitrogen.
        """
        try:
            self._deltaChemshiftN = tuple([dN - self.chemshiftN[0] for dN in self.chemshiftN[1:]])
            return self._deltaChemshiftN
        except IndexError as missingDataError:
            sys.stderr.write("Could not calculate chem shift variation for residue %s : missing N chem shift data" % self.position)
            exit(1)

    @property
    def deltaChemshift(self):
        """
        Returns a tuple of deltaChemshift as tuple like (deltaH, deltaN)
        """
        return tuple(zip(self.deltaChemshiftH, self.deltaChemshiftN))

    @property
    def chemshift(self):
        "Tuple of tuples (chem shift H, chem shift N) for each titration step"
        return tuple(zip(self.chemshiftH,self.chemshiftN))

    @property 
    def chemshiftIntensity(self):
        """
        Calculate chemical shift intensity at each titration step from chemical shift values for hydrogen and nitrogen. 
        """
        self._chemshiftIntensity = tuple([math.sqrt(ddH**2 + (ddN/5)**2) for (ddH, ddN) in self.deltaChemshift])
        return self._chemshiftIntensity


    @property
    def arrow(self):
        "Chem shift vector start/end coords calculated on first and last step chem shift data"
        return (self.chemshiftH[0],
                self.chemshiftN[0],
                self.chemshiftH[-1] - self.chemshiftH[0],
                self.chemshiftN[-1] - self.chemshiftN[0])

    @property
    def rangeH(self):
        "Distance between max and min H chem shift"
        return max(self.chemshiftH) - min(self.chemshiftH)

    @property
    def rangeN(self):
        "Distance between max and min N chem shift"
        return max(self.chemshiftN) - min(self.chemshiftN)
