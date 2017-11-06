#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as num
from classes.widgets import CutOffCursor


class BaseHist(object):
	"""
	Base histogram class, providing interface to a matplotlib figure.
	"""
	# flag for open/closed state
	closed = True
	cutOff = None
	bars = list()
	selected = dict()

	def __init__(self, xAxis, yAxis):
		"Init new matplotlib figure, setup widget, events, and layout"
		self.figure = plt.figure()
		self.xAxis, self.yAxis = list(xAxis), list(yAxis)

		# Tick every 10
		self.positionTicks=range(min(xAxis) - max(xAxis) % 5, max(xAxis)+10, 10)
		
		# Init subplots and plotting data.
		# Must be redefined in child classes
		self.setup_axes()

		# set xy labels
		self.xlabel = self.figure.axes[-1].set_xlabel('Residue')
		self.ylabel = self.figure.text(0.04, 0.5, 'Chem Shift Intensity',
										va='center', rotation='vertical')

		# Init cursor widget and connect it
		self.init_cursor()
		self.init_close_event()
		cutOffStr = "Cut-off : %.4f" if self.cutOff is not None else "Cut-off : %s"
		self.cutOffText = self.figure.text(0.13, 0.9, cutOffStr % self.cutOff)
		# initial draw
		self.figure.canvas.draw()

	def init_close_event(self):
		"Capture window close event"
		self.figure.canvas.mpl_connect('close_event', self.handle_close)
		self.figure.canvas.mpl_connect('draw_event', self.on_draw)

	def on_draw(self, event):
		"Prevent cut off hiding, e.g on window resize"
		self.cursor.visible = True
		self.cursor.update_lines(None, self.cutOff)

	def handle_close(self, event):
		"Set closed state to true on window close"
		self.closed = True

	def close(self):
		"Close figure window"
		plt.close(self.figure)

	def init_cursor(self):
		"""
		Init cursor widget and connect it to self.on_cutoff_update
		"""
		self.cursor = CutOffCursor(self.figure.canvas, self.figure.axes,
									color='r', linestyle='--', lw=0.8,
									horizOn=True, vertOn=False )
		self.cursor.on_changed(self.on_cutoff_update)
		if self.cutOff:
			self.set_cutoff(self.cutOff)

	def show(self):
		"Show figure and set open/closed state"
		self.figure.show()
		self.closed = False

	def setup_axes(self):
		"""
		Should define subplots in figure as well as plotting data.
		Must be replaced in child classes.
		"""
		pass

	def add_cutoff_listener(self, func, mouseUpdateOnly=False):
		"Add extra on_change cutoff event handlers"
		if mouseUpdateOnly:
			self.cursor.on_mouse_update(func)
		else:
			self.cursor.on_changed(func)

	def on_cutoff_update(self, cutOff):
		"""
		Listener method to be connected to cursor widget
		"""
		self.cutOff = cutOff
		cutOffStr = "Cut-off : %.4f" if self.cutOff is not None else "Cut-off : %s"
		self.cutOffText.set_text(cutOffStr % self.cutOff)
		#print("CutOff : %s" % self.cutOff)
		self.draw()

	def set_cutoff(self, cutOff):
		"""
		Cut off setter.
		Triggers change of cut off cursor value, allowing to update figure content.
		kwargs are passed to cursor widget set_cutoff method.
		"""
		if self.closed :
			self.cutOff = cutOff
		else:
			self.cursor.set_cutoff(cutOff)

	def draw(self):
		"""
		Updates bars color according to current cut off value.
		"""
		for ax, axBar in zip(self.figure.axes, self.bars):
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
		self.figure.canvas.draw()


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


	def setup_axes(self):
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
			stepLabel = "%s." % str(index+1)
			ax.set_ylabel(stepLabel, rotation="horizontal", labelpad=15)
			ax.yaxis.set_label_position('right')
			#ax.yaxis.label.set_color('red')
			#self.background.append(self.figure.canvas.copy_from_bbox(ax.bbox))
			self.bars.append(ax.bar(self.xAxis, self.yAxis[index], align='center', alpha=1))
		#self.figure.subplots_adjust(left=0.15)


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

	def setup_axes(self):
		"""
		Create a single subplot and set its layout and data.
		"""
		self.figure.subplots(nrows=1, ncols=1, squeeze=True)
		ax = self.figure.axes[0]
		ax.set_xticks(self.positionTicks)
		maxVal = num.amax(self.yAxis)
		ax.set_ylim(0, num.round(maxVal + maxVal*0.1, decimals=1))
		#self.background.append(self.figure.canvas.copy_from_bbox(ax.bbox))
		self.bars.append(ax.bar(self.xAxis, self.yAxis, align='center', alpha=1))
