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
		If chemShiftH and chemShiftN are provided, use them to start both chemical shift lists.
		"""
		self.position = int(kwargs["position"])
		self.chemShiftH = [float(kwargs["chemShiftH"])] if kwargs.get("chemShiftH") else []
		self.chemShiftN = [float(kwargs["chemShiftN"])] if kwargs.get("chemShiftN") else []
		self._deltaChemShiftH = None
		self._deltaChemShiftN = None
		self._chemShiftIntensity = None

	def __str__(self):
		return str((self.position, self.chemShiftH, self.chemShiftN))

	def __repr__(self):
		return self.__str__()

	def addShift(self, **kwargs):
		"""
		Append chemical shifts to object's lists of chemical shifts
		If one of the values is missing, None or 0, it is ignored.
		"""
		if kwargs.get("chemShiftH") and float(kwargs["chemShiftH"]) != 0:
			self.chemShiftH.append(float(kwargs["chemShiftH"]))
		if kwargs.get("chemShiftN") and float(kwargs["chemShiftN"]) != 0:
			self.chemShiftN.append(float(kwargs["chemShiftN"]))

	def validate(self, titrationSteps):
		"""
		Checks wether an AminoAcid object contains all chemical shift data (1 for each titration step)
		"""
		return True if len(self.chemShiftH) == len(self.chemShiftN) == titrationSteps else False

	@property
	def deltaChemShiftH(self):
		"""
		Calculates distance to the reference for each chemical shift only once for hydrogen.
		"""
		try :
			self._deltaChemShiftH = tuple([dH - self.chemShiftH[0] for dH in self.chemShiftH[1:]])
			return self._deltaChemShiftH
		except IndexError as missingDataError:
			sys.stderr.write("Could not calculate chem shift variation for residue %s : missing H chem shift data" % self.position)
			exit(1)


	@property
	def deltaChemShiftN(self):
		"""
		Calculates distance to the reference for each chemical shift only once for nitrogen.
		"""
		try:
			self._deltaChemShiftN = tuple([dN - self.chemShiftN[0] for dN in self.chemShiftN[1:]])
			return self._deltaChemShiftN
		except IndexError as missingDataError:
			sys.stderr.write("Could not calculate chem shift variation for residue %s : missing N chem shift data" % self.position)
			exit(1)

	@property
	def deltaChemShift(self):
		"""
		Returns a tuple of deltaChemShift as tuple like (deltaH, deltaN)
		"""
		return tuple(zip(self.deltaChemShiftH, self.deltaChemShiftN))

	@property 
	def chemShiftIntensity(self):
		"""
		Calculate chemical shift intensity at each titration step from chemical shift values for hydrogen and nitrogen. 
		"""
		self._chemShiftIntensity = tuple([math.sqrt(ddH**2 + (ddN/5)**2) for (ddH, ddN) in self.deltaChemShift])
		return self._chemShiftIntensity

	def getShiftBounds(self, dim=None):
		"Return (min, max) shift value for each dimension"
		if dim is None:
			return {
				'H':(min(self.chemShiftH), max(self.chemShiftH)),
				'N':(min(self.chemShiftN), max(self.chemShiftN))
			}
		elif dim=='H':
			return (min(self.chemShiftH), max(self.chemShiftH))
		elif dim=='N':
			return (min(self.chemShiftN), max(self.chemShiftN))

	@property
	def arrow(self):
		return (self.chemShiftH[0],
				self.chemShiftN[0], 
				(self.chemShiftH[-1] - self.chemShiftH[0]), 
				(self.chemShiftN[-1] - self.chemShiftN[0]))

	@property
	def rangeH(self):
		return max(self.chemShiftH) - min(self.chemShiftH)

	@property
	def rangeN(self):
		return max(self.chemShiftN) - min(self.chemShiftN)
