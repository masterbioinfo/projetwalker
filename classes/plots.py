#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as num
from classes.widgets import CutOffCursor


class BaseFig(object):


    def __init__(self, xaxis, yaxis):
        "Init new figure"
        self.figure = plt.figure()
        self.closed = True
        self.xaxis = list(xaxis)
        self.yaxis = list(yaxis)
        self.setup_axes()

    def show(self):
        "Show figure and set open/closed state"
        self.figure.show()
        self.closed = False

    def close(self):
        "Close figure window"
        plt.close(self.figure)

    def init_events(self):
        "Capture window close event"
        self.figure.canvas.mpl_connect('close_event', self.on_close)
        self.figure.canvas.mpl_connect('draw_event', self.on_draw)

    def on_close(self, event):
        "Set closed state to true on window close"
        self.closed = True

## ------------------------
## Placeholders

    def setup_axes(self):
        """
        Should define subplots in figure as well as plotting data.
        Must be replaced in child classes.
        """
        pass

    def on_draw(self, event):
        pass



class BaseHist(BaseFig):
    """
    Base histogram class, providing interface to a matplotlib figure.
    """

    cutoff = None # flag for open/closed state

    def __init__(self, xaxis, yaxis):
        "Init new matplotlib figure, setup widget, events, and layout"

        # Tick every 10
        self.positionTicks=range(min(xaxis) - max(xaxis) % 5, max(xaxis)+10, 10)
        self.filtered = dict()
        self.bars = list()
        super().__init__(xaxis, yaxis)

        self.xlabel = self.figure.axes[-1].set_xlabel('Residue')
        self.ylabel = self.figure.text(0.04, 0.5, 'Chem Shift Intensity',
                            va='center', rotation='vertical')

        # Init cursor widget and connect it
        self.init_cursor()
        self.init_events()
        self.cutoffText = self.figure.text(0.13, 0.9, self.cutoff_str)

        # initial draw
        self.figure.canvas.draw()

    @property
    def cutoff_str(self):
        if self.cutoff is not None:
            return "Cut-off : {cutoff:.4f}".format(cutoff=self.cutoff)
        else:
            return "Cut-off : {cutoff}".format(cutoff=self.cutoff)

    def on_draw(self, event):
        "Prevent cut off hiding, e.g on window resize"
        self.cursor.visible = True
        self.cursor.update_lines(None, self.cutoff)

    def init_cursor(self):
        """
        Init cursor widget and connect it to self.on_cutoff_update
        """
        self.cursor = CutOffCursor(self.figure.canvas, self.figure.axes,
                                    color='r', linestyle='--', lw=0.8,
                                    horizOn=True, vertOn=False )
        self.cursor.on_changed(self.on_cutoff_update)
        if self.cutoff:
            self.set_cutoff(self.cutoff)

    def add_cutoff_listener(self, func, mouseUpdateOnly=False):
        "Add extra on_change cutoff event handlers"
        if mouseUpdateOnly:
            self.cursor.on_mouse_update(func)
        else:
            self.cursor.on_changed(func)

    def on_cutoff_update(self, cutoff):
        """
        Listener method to be connected to cursor widget
        """
        BaseHist.cutoff = cutoff
        self.cutoffText.set_text(self.cutoff_str)
        self.draw()

    def set_cutoff(self, cutoff):
        """
        Cut off setter.
        Triggers change of cut off cursor value, allowing to update figure content.
        kwargs are passed to cursor widget set_cutoff method.
        """
        BaseHist.cutoff = cutoff
        if not self.closed:
            self.cursor.set_cutoff(cutoff)

    def draw(self):
        """
        Updates bars color according to current cut off value.
        """
        for ax, axBar in zip(self.figure.axes, self.bars):
            for bar in axBar:
                if self.cutoff:
                    if bar.get_height() >= self.cutoff: # show high intensity residues
                        if not self.filtered.get(bar):
                            bar.set_facecolor('orange')
                            self.filtered[bar] = 1
                    else:
                        if self.filtered.get(bar):
                            bar.set_facecolor(None)
                            self.filtered[bar] = 0
        self.figure.canvas.draw()


class MultiHist(BaseHist):
    """
    BaseHist child class for plotting stacked hists.
    """

    def __init__(self, xaxis, yMatrix):
        """
        Sets title
        """
        super().__init__(xaxis, yMatrix)
        self.figure.suptitle('Titration : steps 1 to {last}'.format(last=len(yMatrix) ) )
        self.figure.text(0.96, 0.5, 'Titration step',
                        va='center', rotation='vertical')

class Hist(BaseHist):
    """
    BaseHist child class for plotting single histogram
    """

    def __init__(self, xaxis, yaxis, step=None):
        """
        Sets title
        """
        super().__init__(xaxis, yaxis)
        if step:
            self.figure.suptitle('Titration step {step}'.format(step=step) )# set title

    def setup_axes(self):
        """
        Create a single subplot and set its layout and data.
        """
        self.figure.subplots(nrows=1, ncols=1, squeeze=True)
        ax = self.figure.axes[0]
        ax.set_xticks(self.positionTicks)
        maxVal = num.amax(self.yaxis)
        ax.set_ylim(0, num.round(maxVal + maxVal*0.1, decimals=1))
        #self.background.append(self.figure.canvas.copy_from_bbox(ax.bbox))
        self.bars.append(ax.bar(self.xaxis, self.yaxis, align='center', alpha=1))

    def setup_axes(self):
        """
        Creates a subplot for each line in yaxis matrix
        """
        self.figure.subplots(nrows=len(self.yaxis), ncols=1,
                            sharex=True, sharey=True, squeeze=True)
        # Set content and layout for each subplot.
        for index, ax in enumerate(self.figure.axes):
            ax.set_xticks(self.positionTicks)
            maxVal = num.amax(self.yaxis)
            ax.set_ylim(0, num.round(maxVal + maxVal*0.1, decimals=1))
            stepLabel = "{step}.".format(step=str(index+1))
            ax.set_ylabel(stepLabel, rotation="horizontal", labelpad=15)
            ax.yaxis.set_label_position('right')
            #ax.yaxis.label.set_color('red')
            #self.background.append(self.figure.canvas.copy_from_bbox(ax.bbox))
            self.bars.append(ax.bar(self.xaxis, self.yaxis[index], align='center', alpha=1))
        #self.figure.subplots_adjust(left=0.15)

