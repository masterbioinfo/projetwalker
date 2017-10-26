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
		self.closed=False
		self.cutOff=None


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
		self.figure.show()


class MultiHist(BaseHist):
	def __init__(self, xAxis, yAxis):
		super().__init__(xAxis, yAxis)
		self.figure.subplots(nrows=len(yAxis), ncols=1, 
								sharex=True, sharey=True, squeeze=True)
		self.ylabel=self.figure.text(0.04, 0.5, 'Chem Shift Intensity', 
							va='center', rotation='vertical') # set common ylabel
		self.xlabel = self.figure.axes[-1].set_xlabel('Residue') # set common xlabel
		self.figure.suptitle('Titration : steps 1 to %s' % len(yAxis) )# set title
		self.positionTicks =range(xAxis[0] - xAxis[0] % 5, xAxis[-1]+10, 10)
		self.selected = dict()
		self.background = [] 
		for index, ax in enumerate(self.figure.axes):
			
			ax.set_xticks(self.positionTicks)
			maxVal = num.amax(yAxis)
			ax.set_ylim(0, num.round(maxVal + maxVal*0.1, decimals=1))
			self.background.append(self.figure.canvas.copy_from_bbox(ax.bbox))
			self.bars.append(ax.bar(xAxis, yAxis[index], align = 'center', alpha = 1))
		self.figure.canvas.draw()
	
		self.cutOff = None
		self.cursor = CutOffCursor(self.figure.canvas, self.figure.axes, 
									color='r', linestyle='--', lw=0.5, 
									horizOn=True, vertOn=False )
		self.cursor.on_changed(self.cutOffListener)
		
	def cutOffListener(self, cutOff):
		self.updateCutOff(cutOff)

	def updateCutOff(self, cutOff):
		self.cutOff = cutOff
		self.draw()

	def setCutOff(self, cutOff):
		self.cursor.setCutOff(cutOff)