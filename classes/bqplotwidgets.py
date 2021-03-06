import bqplot
import math
from itertools import chain
from ipywidgets import *
import numpy as np
from classes.ipywidgets import TitrationWidget, PanelContainer




class IntensityBarPlot(TitrationWidget, bqplot.Figure):

    def __init__(self, step, stacked=False, *args, **kwargs):

        self.step = step

        self.x_scale = bqplot.OrdinalScale()
        self.y_scale = bqplot.LinearScale(min=0, max = max(chain.from_iterable(self.titration.intensities))*1.1)

        self.x_data = sorted(self.titration.complete.keys())
        self.y_data = self.titration.intensities[self.step]

        self.ax_x = bqplot.Axis(
            label="Residues",
            scale=self.x_scale,
            grid_lines='none',
            num_ticks=math.ceil(len(self.x_data)/10),
            #visible = not stacked
        )

        #

        self.ax_y = bqplot.Axis(
            #label="Intensity",
            scale=self.y_scale,
            orientation='vertical',
            tick_format='0.2f',
            grid_lines='dashed',
            grid_color='#D1D0CE',
            #visible = not stacked
        )


        self.bar_chart = bqplot.Bars(
            x=self.x_data,
            y=self.y_data,
            colors=['#38ACEC'],
            stroke='#FFFFFF',
            scales= {'x': self.x_scale, 'y': self.y_scale},
            selected_style={'stroke': 'white', 'fill': 'orange'},
            interactions = {
                'legend_hover': 'highlight_axes',
                'hover': 'tooltip',
                #'click': 'select',
            }
        )
            #labels=["Chemical Shift"],
            #display_legend=True)

        self.cutoff = bqplot.Lines(
            x=[min(self.x_data), max(self.x_data)] ,
            y=[0.1, 0.1],
            scales = {
                'x': self.x_scale,
                'y':self.y_scale
            },
            colors=['red'],
            opacities = [0.7],
            stroke_width=1.5,
            line_style="dashed"

        )
        if self.titration.cutoff:
            self.update_cutoff()
        else:
            self.set_cutoff()

        self.set_tooltips()

        layout = kwargs.get('layout', Layout(width='100%', height= "95%"))
        kwargs['layout'] = layout

        bqplot.Figure.__init__(
            self,
            marks=[self.bar_chart, self.cutoff],
            axes=[self.ax_x, self.ax_y],
            title="Chemical shift intensity per residue",
            *args, **kwargs)

    def set_tooltips(self):
        # Adding a tooltip on hover in addition to select on click
        def_tt = bqplot.Tooltip(
            fields=['x', 'y'],
            formats=['', '.2f'],
            labels=('Residue', 'Intensity'))
        self.bar_chart.tooltip=def_tt
        self.bar_chart.interactions = {
            'legend_hover': 'highlight_axes',
            'hover': 'tooltip',
            'click': 'select',
        }

    def set_cutoff(self, change=None):
        new_cutoff = change['new'] if change is not None else 0.1
        self.titration.cutoff=new_cutoff
        self.update_cutoff()

    def update_cutoff(self):
        self.cutoff.y = [self.titration.cutoff]*2
        selection = []
        for idx, intensity in enumerate(self.bar_chart.y):
            if intensity >= self.titration.cutoff:
                selection.append(idx)
        self.bar_chart.selected = selection

    def set_step(self, change):
        self.step = change['new']
        self.bar_chart.y = self.titration.intensities[self.step]
        self.update_cutoff()


class CutoffSlider(TitrationWidget, FloatSlider):

    def __init__(self, *args, **kwargs):

        self.update_kwargs(kwargs)
        FloatSlider.__init__(self, *args, **kwargs)

    def update_kwargs(self, kwargs):
        kwargs.update({
            'min': 0,
            'max': max(chain.from_iterable(self.titration.intensities))*1.1,
            'step': 0.01,
            'value' : self.titration.cutoff or 0.1,
            'orientation': 'vertical',
            'read_out': True,
            'readout_format': '.2f',
            'layout' : Layout(height='95%', padding='30px 0px 30px 0px'),
            'description':"Cut-off"
        })



class IntensityPlot(TitrationWidget, HBox):

    def __init__(self, step = None, *args, **kwargs):

        HBox.__init__(self, *args, **kwargs)

        self.layout=Layout(height='600px')

        self.step = step or self.titration.dataSteps - 1
        self.slider = CutoffSlider()
        self.stepSlider = IntSlider(
            min=1,
            max=self.titration.dataSteps -1,
            step=1,
            value=self.step,
            description="Step",
            orientation='vertical',
            readout=True,
            layout=Layout(
                height='95%',
                padding='30px 0px 30px 0px')
        )
        self.plot = IntensityBarPlot(step=self.step)
        self.slider.observe(self.plot.set_cutoff, 'value')
        self.stepSlider.observe(self.plot.set_step, 'value')


        self.children = (self.stepSlider, self.slider, self.plot)


class IntensityPanel(TitrationWidget, PanelContainer):
    def __init__(self, *args, **kwargs):
        PanelContainer.__init__(self, *args, **kwargs)

        self.add_class('intensity-panel')

        self.label = Label("Chemical shift intensities")
        self.label.add_class('panel-header-title')

        self.plot_widgets = IntensityPlot()

        #self.toolbar = bqplot.Toolbar(figure= self.plot_widgets.plot)

        self.set_heading([self.label])

        self.set_content([self.plot_widgets])



class ShiftMap(bqplot.Figure, TitrationWidget):

    def __init__(self, *args, **kwargs):

        bqplot.Figure.__init__(
            self,
            #marks=[self.scatter],
            #axes=[self.ax_x, self.ax_y, self.ax_c],
            title="Chemical shifts",
            *args, **kwargs)

        self.update()

        self.layout=Layout(width='100%', height='600px')

    def set_tooltips(self):
        # Adding a tooltip on hover in addition to select on click
        def_tt = bqplot.Tooltip(
            fields=['name', 'x', 'y', 'color'],
            formats=['', '.2f', '.2f', ''],
            labels=['Residue', 'H', 'N', 'Step'])
        self.scatter.tooltip=def_tt
        self.scatter.interactions = {
            'legend_hover': 'highlight_axes',
            'hover': 'tooltip',
            'click': 'select',
        }

    def update(self):
        self.residues = self.titration.filtered.values()
        if not self.residues:
            return

        self.x_scale = bqplot.LinearScale(
            min = min(chain.from_iterable([res.chemshiftH for res in self.residues])) * 0.99,
            max = max(chain.from_iterable([res.chemshiftH for res in self.residues])) * 1.01
        )
        self.y_scale = bqplot.LinearScale(
            min = min(chain.from_iterable([res.chemshiftN for res in self.residues])) * 0.98,
            max = max(chain.from_iterable([res.chemshiftN for res in self.residues])) * 1.02
        )
        self.c_scale = bqplot.ColorScale(scheme='Purples')

        self.ax_x = bqplot.Axis(
            label="Proton chemical shifts",
            scale=self.x_scale,
            tick_format='0.2f',
            grid_lines='dashed',
            grid_color='#D1D0CE',
            num_ticks=10
            #visible = not stacked
        )

        self.ax_y = bqplot.Axis(
            label="Azote chemical shifts",
            scale=self.y_scale,
            orientation='vertical',
            tick_format='0.2f',
            grid_lines='dashed',
            grid_color='#D1D0CE',
            num_ticks=10
            #visible = not stacked
        )

        self.ax_c = bqplot.ColorAxis(
            label_location='middle',
            scale=self.c_scale,
            orientation='vertical',
            side='right',
            label="Step",
            #label_color = 'blue',
            offset = {'scale':self.x_scale,'value':0}
        )

        self.x_data = []
        self.y_data = []
        self.c_data = []
        names = []

        for res in self.residues:
            self.x_data += res.chemshiftH
            self.y_data += res.chemshiftN
            self.c_data += list(range(self.titration.dataSteps))
            names += [str(res.position)]*len(res.chemshiftH)

        self.scatter = bqplot.Scatter(
            x=self.x_data,
            y=self.y_data,
            color=self.c_data,
            marker='circle',
            stroke='#FFFFFF',
            names=names,
            display_names=False,
            names_unique=False,
            #default_opacities = np.linspace(0.1, 0.8, num=self.titration.dataSteps).tolist(),
            stroke_width = 0,
            scales= {'x': self.x_scale, 'y': self.y_scale, 'color':self.c_scale},
            selected_style={'stroke': 'white', 'fill': 'orange'},
            interactions = {
                'legend_hover': 'highlight_axes',
                'hover': 'tooltip',
                #'click': 'select',
            }
        )

        self.set_tooltips()
        self.marks = [self.scatter]
        self.axes=[self.ax_x, self.ax_y, self.ax_c]


class TitrationCurve(TitrationWidget, bqplot.Figure):

    def __init__(self, residue = None, *args, **kwargs):
        bqplot.Figure.__init__(self, *args, **kwargs)
        self.x_scale = bqplot.LinearScale(
            min = 0
        )
        self.y_scale = bqplot.LinearScale(
            min = 0
        )
        # self.c_scale = bqplot.ColorScale(scheme='Purples')

        self.ax_x = bqplot.Axis(
            label="[ratio]",
            scale=self.x_scale,
            tick_format='0.2f',
            grid_lines='dashed',
            grid_color='#D1D0CE'
            #visible = not stacked
        )

        self.ax_y = bqplot.Axis(
            label="Chemical shift intensity",
            scale=self.y_scale,
            orientation='vertical',
            tick_format='0.2f',
            grid_lines='dashed',
            grid_color='#D1D0CE'
            #visible = not stacked
        )

        self.res = self.titration.complete[residue]

        self.x_data = self.titration.protocole.iloc[:, [5]].values.T.tolist().pop() # concentration ratios
        self.y_data = self.res.chemshiftIntensity

        self.scatter = bqplot.Scatter(
            x=self.x_data,
            y=self.y_data,
            marker='circle',
            stroke='#FFFFFF',
            #names=names,
            display_names=False,
            names_unique=False,
            #default_opacities = np.linspace(0.1, 0.8, num=self.titration.dataSteps).tolist(),
            stroke_width = 0,
            scales= {'x': self.x_scale, 'y': self.y_scale},
            selected_style={'stroke': 'white', 'fill': 'orange'},
            interactions = {
                'legend_hover': 'highlight_axes',
                'hover': 'tooltip',
                #'click': 'select',
            }
        )

        self.marks = [self.scatter]
        self.axes=[self.ax_x, self.ax_y]

    def change_res(self, change):
        self.res = self.titration.complete[change['new']]
        self.update()

    def update(self):
        self.scatter.x = self.titration.protocole.iloc[:, [5]].values.T.tolist().pop()
        self.scatter.y = self.res.chemshiftIntensity
        self.set_tooltips()

    def set_tooltips(self):
        # Adding a tooltip on hover in addition to select on click
        def_tt = bqplot.Tooltip(
            fields=['x', 'y'],
            formats=['.2f', '.2f'],
            labels=['Ratio', 'Intensity'])
        self.scatter.tooltip=def_tt
        self.scatter.interactions = {
            'legend_hover': 'highlight_axes',
            'hover': 'tooltip',
            'click': 'select',
        }


class TitrationCurveOperator(TitrationWidget, VBox):

    def __init__(self, *args, **kwargs):
        VBox.__init__(self, *args, **kwargs)

        self.dropdown = Dropdown(
            options = sorted(self.filtered),
            description='Residue:',
            disabled=False,
            value= min(self.filtered)if self.filtered else None,
            tooltip='Pick a residue to plot'
        )

        self.filter= ToggleButton(
            value=True,
            description='Filtered',
            disabled=False,
            button_style='primary',
            icon='dot-circle-o',
            tooltip='Restrict options to filtered residues'
        )
        self.filter.observe(self.switch_filter, 'value')

        self.textinput = BoundedIntText(
            description='Residue:',
            disabled=False,
            value=min(self.titration.complete.keys()),
            min=min(self.titration.complete.keys()),
            max=max(self.titration.complete.keys()),
            tooltip='Pick a residue to plot'
        )

        #self.layout = Layout(width='50%')

        residue = self.dropdown.value if self.filter.value and self.filtered else self.textinput.value

        self.curve = TitrationCurve(residue)

        self.dropdown.observe(self.curve.change_res, 'value')
        self.textinput.observe(self.validate_res_text, 'value')

        self.toolbar = HBox([self.dropdown,self.filter])

        self.children = [self.toolbar, self.curve]

        self.update()

    @property
    def filtered(self):
        return sorted(self.titration.filtered.keys())

    def update(self):
        if not self.filtered:
            self.filter.value=False
            self.filter.disabled=True
        else:
            self.filter.disabled=False
        if self.filter.value:
            self.curve.change_res({'new': self.dropdown.value})
            self.dropdown.options = self.filtered
        else:
            self.curve.change_res({'new': self.textinput.value})

    def validate_res_text(self, change):
        if change['new'] not in self.titration.complete:
            if change['old'] <= change['new']:
                change['new'] += 1
            else:
                change['new'] -=1
            self.textinput.value = change['new']
        else:
            self.curve.change_res(change)

    def switch_filter(self, change):
        if change['new']:
            self.filter.icon='dot-circle-o'
            self.toolbar.children = [self.dropdown, self.filter]
        else:
            self.filter.icon='circle-o'
            self.toolbar.children = [self.textinput, self.filter]
        self.update()


class CurveContainer(TitrationWidget, HBox):

    def __init__(self, *args, **kwargs):
        HBox.__init__(self, *args, **kwargs)

        self.curves = [
            TitrationCurveOperator(),
            TitrationCurveOperator()
        ]

        self.children = self.curves

    def update(self):
        for child in self.children:
            child.update()



class ChemshiftPanel(TitrationWidget, PanelContainer):
    def __init__(self, uploader=None, *args, **kwargs):
        PanelContainer.__init__(self, *args, **kwargs)

        self.uploader= uploader

        self.add_class('intensity-panel')

        self.label = Label("Data visualization")
        self.label.add_class('panel-header-title')

        tab_titles = ['Intensities', "Shiftmap", 'Titration curves']
        self.tabs = Tab()

        for num, title in enumerate(tab_titles):
            self.tabs.set_title(num, title)

        #self.toolbar = bqplot.Toolbar(figure= self.plot_widgets.plot)

        self.set_heading([self.label])

        self.tabs.observe(self.tab_switch, 'selected_index')

        self.placeholder = VBox([
            HTML(
                "<h2>Titration files are not loaded.</h2>"
                "<p>No data to display.</p>"
                ""
            )])
        if self.uploader:
            self.placeholder.children += (self.uploader,)
            self.uploader.add_observer(self.update)

        self.placeholder.add_class('well')
        self.placeholder.add_class('plot-placeholder')

        self.shiftmap_placeholder = HTML(
            "<h2>No residues to show in shiftmap.</h2>"
            "<p>Select residues to show using the cutoff slider in <code>Intensity</code> tab.</p>"
            "<p>You may also select specific residues by clicking on bars (<code>Ctrl+click</code> to add)</p>")
        self.shiftmap_placeholder.add_class('well')
        self.shiftmap_placeholder.add_class('plot-placeholder')

        # initialize content
        self.update()

    def tab_switch(self, change):
        if change['new'] == 1:
            if self.titration.filtered:
                self.shiftmap.update()
                self.tabs.children = [self.plot_widgets, self.shiftmap, self.curves]
            else:
                self.tabs.children = [self.plot_widgets, self.shiftmap_placeholder, self.curves]
        elif change['new'] == 2:
            self.curves.update()

    def update(self):
        if self.titration.files:
            self.plot_widgets = IntensityPlot()
            self.shiftmap = ShiftMap()
            self.curves = CurveContainer()
            self.tabs.children = [self.plot_widgets, self.shiftmap, self.curves]
            self.set_content([self.tabs])
        else:
            self.set_content([self.placeholder])
        self.update_curves()

    def update_curves(self, change=None):
        if hasattr(self, 'curves'):
            self.curves.update()
