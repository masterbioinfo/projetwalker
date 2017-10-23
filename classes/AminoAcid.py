import math

class AminoAcid(object):
	"""
	Class AminoAcid
	Describes a amino-acid using its position number in the proteic sequence.
	An AminoAcid object contains the values of measured chemical shift at each titration step. 
	These data are split in two lists, one contains the hydrogen chem shift data, the other contains nitrogen chem shifts data.
	The first element of each list is used as a reference value for calculating difference in chemical shifts at each titration step, i.e measured chem shift - ref chem shift. 
	"""

	def __init__(self, **kwargs):
		self.position = kwargs["residue"]
		self.chemShiftH = [float(kwargs["chemicalShiftH"])]
		self.chemShiftN = [float(kwargs["chemicalShiftN"])]
		self._deltaChemShiftH = None
		self._deltaChemShiftN = None
		self._chemShiftIntensity = None

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
		if self._deltaChemShiftH is None:
			self._deltaChemShiftH = list()
			j = 0
			while j < len(self.chemShiftH):
				self._deltaChemShiftH.append(self.chemShiftH[j] - self.chemShiftH[0])
				j += 1
		return self._deltaChemShiftH

	@property
	def deltaChemShiftN(self):
		"""
		Calculates distance to the reference for each chemical shift only once for nitrogen.
		"""
		if self._deltaChemShiftN is None:
			self._deltaChemShiftN = list()
			j = 0
			while j < len(self.chemShiftN):
				self._deltaChemShiftN.append(self.chemShiftN[j] - self.chemShiftN[0])
				j += 1
		return self._deltaChemShiftN

	@property
	def deltaFinal(self):
		"""
		Get distance to the reference for each chemical shift at the final titration step. 
		"""
		return (self.deltaChemShiftH[-1], self.deltaChemShiftN[-1])

	@property 
	def chemShiftIntensity(self):
		"""
		Calculate chemical shift intensity at each titration step from chemical shift values for hydrogen and nitrogen. 
		"""
		if self._chemShiftIntensity is None:
			self._chemShiftIntensity = list()
			i = 0
			while i < len(self.deltaChemShiftH):
				self._chemShiftIntensity.append(math.sqrt(self.deltaChemShiftH[i] ** 2 + (self.deltaChemShiftN[i]/5)**2 ))
				i += 1
		return self._chemShiftIntensity
