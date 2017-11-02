#!/usr/bin/python3

import matplotlib.pyplot as plt
from matplotlib.widgets import MultiCursor, Slider
from classes.widgets import CutOffCursor
import itertools
import numpy as num
from math import *


class BaseHist(object):
	"""
	Base histogram class, providing interface to a matplotlib figure.
	"""
	def __init__(self, xAxis, yAxis):
		self.figure = plt.figure()
		self.closed=True
		
		self.bars = []
		self.selected = dict()
		self.background = [] 
		self.cutOff=None
		self.cutOffDrawn = False

		# Tick every 10
		self.positionTicks=range(xAxis[0] - xAxis[0] % 5, xAxis[-1]+10, 10)
		self.xAxis, self.yAxis = xAxis, yAxis

		# Init subplots and plotting data.
		# Must be redefined in child classes
		self.setupAxes()

		# set xy labels
		self.xlabel = self.figure.axes[-1].set_xlabel('Residue') 
		self.ylabel=self.figure.text(0.04, 0.5, 'Chem Shift Intensity', 
									va='center', rotation='vertical') 

		# Init cursor widget and connect it
		self.initCursor()
		self.initCloseEvent()

		# initial draw
		self.figure.canvas.draw()
	
	def initCloseEvent(self):
		"Capture window close event"
		self.figure.canvas.mpl_connect('close_event', self.handle_close)

	def handle_close(self, event):
		"Set closed state to true on window close"
		self.closed=True

	def close(self):
		"Close figure window"
		plt.close(self.figure)

	def initCursor(self):
		"""
		Init cursor widget and connect it to self.cutOffListener
		"""
		self.cursor = CutOffCursor(self.figure.canvas, self.figure.axes, 
									color='r', linestyle='--', lw=0.8, 
									horizOn=True, vertOn=False )
		self.cursor.on_changed(self.cutOffListener)
		if self.cutOff:
			self.setCutOff(self.cutOff)

	def show(self):
		"Show figure and set open/closed state"
		self.figure.show()
		self.closed = False

	def setupAxes(self, yAxis):
		"""
		Should define subplots in figure as well as plotting data.
		Must be replaced in child classes.
		"""
		pass

	def addCutOffListener(self, func):
		"Add extra on_change cutoff event handlers"
		self.cursor.on_changed(func)

	def cutOffListener(self, cutOff):
		"""
		Listener method to be connected to cursor widget
		"""
		self.cutOff = cutOff
		print("CutOff : %s" % self.cutOff)
		self.draw()		

	def setCutOff(self, cutOff):
		"""
		Cut off setter. 
		Triggers change of cut off cursor value,
		allowing to update figure content.
		"""
		if self.closed : 
			self.cutOff = cutOff
			self.cutOffDrawn = False
		else:
			self.cursor.setCutOff(cutOff)
			self.cutOffDrawn = True

	def draw(self):
		"""
		Updates bars color according to current cut off value. 
		"""
		#plt.ioff()
		for i, (ax, axBar) in enumerate(zip(self.figure.axes, self.bars)):	
			#self.figure.canvas.restore_region(self.background[i])
			for bar in axBar:
				if self.cutOff:
					if bar.get_height() >= self.cutOff: # show high intensity residues
						if not self.selected.get(bar):
							bar.set_facecolor('orange')
							self.selected[bar] = 1
					else:
						if self.selected.get(bar):
							bar.set_facecolor(None)
							self.selected[bar] = 0
				#ax.draw_artist(bar)
				#bar.set_animated(False)
				#self.figure.canvas.blit(ax.bbox)
		self.figure.canvas.draw()
		#plt.ion()
		


class MultiHist(BaseHist):
	"""
	BaseHist child class for plotting stacked hists.
	"""
	def __init__(self, xAxis, yMatrix):
		"""
		Sets title
		"""
		super().__init__(xAxis, yMatrix)
		self.figure.suptitle('Titration : steps 1 to %s' % len(yMatrix) )


	def setupAxes(self):
		"""
		Creates a subplot for each line in yAxis matrix
		"""
		self.figure.subplots(nrows=len(self.yAxis), ncols=1, 
							sharex=True, sharey=True, squeeze=True)
		# Set content and layout for each subplot.
		for index, ax in enumerate(self.figure.axes):
			ax.set_xticks(self.positionTicks)
			maxVal = num.amax(self.yAxis)
			ax.set_ylim(0, num.round(maxVal + maxVal*0.1, decimals=1))
			self.background.append(self.figure.canvas.copy_from_bbox(ax.bbox))
			self.bars.append(ax.bar(self.xAxis, self.yAxis[index], align = 'center', alpha = 1))


class Hist(BaseHist):
	"""
	BaseHist child class for plotting single histogram
	"""

	def __init__(self, xAxis, yAxis, step=None):
		"""
		Sets title
		"""
		super().__init__(xAxis, yAxis)
		if step:
			self.figure.suptitle('Titration step %s' % step )# set title

	def setupAxes(self):
		"""
		Create a single subplot and set its layout and data. 
		"""
		self.figure.subplots(nrows=1, ncols=1, squeeze=True)
		ax = self.figure.axes[0]
		ax.set_xticks(self.positionTicks)
		maxVal = num.amax(self.yAxis)
		ax.set_ylim(0, num.round(maxVal + maxVal*0.1, decimals=1))
		self.background.append(self.figure.canvas.copy_from_bbox(ax.bbox))
		self.bars.append(ax.bar(self.xAxis, self.yAxis, align = 'center', alpha = 1))
