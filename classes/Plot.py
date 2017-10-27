#!/usr/bin/python3

import matplotlib.pyplot as plt
from matplotlib.widgets import MultiCursor, Slider
from classes.MultiDraggableCursor import CutOffCursor
import itertools
import numpy as num

class BaseHist(object):
	def __init__(self, xAxis, yAxis):
		self.figure = plt.figure()
		self.bars = []
		self.selected = dict()
		self.background = [] 
		self.closed=False
		self.cutOff=None
		self.positionTicks=range(xAxis[0] - xAxis[0] % 5, xAxis[-1]+10, 10)
		self.xAxis, self.yAxis = xAxis, yAxis
		self.setupAxes()

		self.ylabel=self.figure.text(0.04, 0.5, 'Chem Shift Intensity', 
									va='center', rotation='vertical') # set common ylabel
		self.xlabel = self.figure.axes[-1].set_xlabel('Residue') # set common xlabel
		
		# Allow us to reopen figure after it's closed
		self.initCloseEvent()
		# Init widgets and connect it
		self.initCursor()
		
	def initCursor(self):
		self.cursor = CutOffCursor(self.figure.canvas, self.figure.axes, 
									color='r', linestyle='--', lw=0.8, 
									horizOn=True, vertOn=False )
		self.cursor.on_changed(self.cutOffListener)
		if self.cutOff:
			self.setCutOff(self.cutOff)

	def initCloseEvent(self):
		self.figure.canvas.mpl_connect('close_event', self.handle_close)

	def handle_close(self, event):
		self.closed=True

	def setupAxes(self, yAxis):
		pass

	def cutOffListener(self, cutOff):
		self.updateCutOff(cutOff)

	def updateCutOff(self, cutOff):
		self.cutOff = cutOff
		print("CutOff change : %s" % self.cutOff)
		self.draw()

	def setCutOff(self, cutOff):
		self.cursor.setCutOff(cutOff)

	def draw(self):
		plt.ioff()
		i=0
		for ax, axBar in zip(self.figure.axes, self.bars):	
			self.figure.canvas.restore_region(self.background[i])
			i+=1
			for bar in axBar:
				if self.cutOff:
					if bar.get_height() >= self.cutOff: # show high intensity residues
						if not self.selected.get(bar):
							bar.set_color('orange')
							self.selected[bar] = 1
					else:
						if self.selected.get(bar):
							bar.set_color(None)
							self.selected[bar] = 0
				ax.draw_artist(bar)
				#bar.set_animated(False)
			#self.figure.canvas.blit(ax.bbox)
		self.figure.canvas.draw()
		plt.ion()

	def show(self):
		if self.closed:
			newFig = plt.figure()
			newManager = newFig.canvas.manager 
			newManager.canvas.figure = self.figure
			self.figure.set_canvas(newManager.canvas)
			self.initCloseEvent()
			self.initCursor()
		else:
			self.figure.show()


class MultiHist(BaseHist):
	def __init__(self, xAxis, yMatrix):
		super().__init__(xAxis, yMatrix)
		self.figure.suptitle('Titration : steps 1 to %s' % len(yMatrix) )# set title
	def setupAxes(self):
		self.figure.subplots(nrows=len(self.yAxis), ncols=1, 
							sharex=True, sharey=True, squeeze=True)
		for index, ax in enumerate(self.figure.axes):
			ax.set_xticks(self.positionTicks)
			maxVal = num.amax(self.yAxis)
			ax.set_ylim(0, num.round(maxVal + maxVal*0.1, decimals=1))
			self.background.append(self.figure.canvas.copy_from_bbox(ax.bbox))
			self.bars.append(ax.bar(self.xAxis, self.yAxis[index], align = 'center', alpha = 1))
		
class Hist(BaseHist):
	def __init__(self, xAxis, yAxis, step=None):
		super().__init__(xAxis, yAxis)
		if step:
			self.figure.suptitle('Titration step %s' % step )# set title

	def setupAxes(self):
		self.figure.subplots(nrows=1, ncols=1, squeeze=True)
		ax = self.figure.axes[0]
		ax.set_xticks(self.positionTicks)
		maxVal = num.amax(self.yAxis)
		ax.set_ylim(0, num.round(maxVal + maxVal*0.1, decimals=1))
		self.background.append(self.figure.canvas.copy_from_bbox(ax.bbox))
		self.bars.append(ax.bar(self.xAxis, self.yAxis, align = 'center', alpha = 1))
