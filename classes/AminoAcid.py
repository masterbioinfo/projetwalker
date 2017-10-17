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
		"""
		Initialize AminoAcid object, only required argument is position.
		If chemShiftH and chemShiftN are provided, use them to start both chemical shift lists.
		"""
		self.position = int(kwargs["position"])
		self.chemShiftH = [float(kwargs["chemShiftH"])] if kwargs.get("chemShiftH") else []
		self.chemShiftN = [float(kwargs.["chemShiftN"])] if kwargs.get("chemShiftN") else []
		self._deltaChemShiftH = None
		self._deltaChemShiftN = None
		self._chemShiftIntensity = None

	def addShift(self, **kwargs):
		"""
		Append chemical shifts to object's lists of chemical shifts
		"""
		self.chemShiftH.append(float(kwargs["chemShiftH"]))
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
		if self._deltaChemShiftH is None:
			self._deltaChemShiftH = tuple([dH - self.chemShiftH[0] for dH in self.chemShiftH])
		return self._deltaChemShiftH

	@property
	def deltaChemShiftN(self):
		"""
		Calculates distance to the reference for each chemical shift only once for nitrogen.
		"""
		if self._deltaChemShiftN is None:
			self._deltaChemShiftN = tuple([dN - self.chemShiftN[0] for dN in self.chemShiftN])
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
			self._chemShiftIntensity = tuple([math.sqrt(ddH**2 + (ddN/5)**2) for (ddH, ddN) in zip(self.deltaChemShiftH,self.deltaChemShiftN)])
		return self._chemShiftIntensity
