from ipywidgets import *
from ipyfileupload.widgets import DirectoryUploadWidget
from traitlets import observe
import base64, io
import pandas as pd

from classes.Titration import Titration

class TitrationWidget(Widget):
    "Root class for titration GUI elements"
    titration=None

    def __init__(self, titration = None, *args, **kwargs):
        self.titration = titration or TitrationWidget.titration
        self.observe(self.on_change, names='value')

    def on_change(self, change):
        "Callback method when the widget value changes"
        pass

    @classmethod
    def settitration(cls, titration):
        cls.titration=titration


class AttrControlMixin(TitrationWidget):
    """Sets an attribute of target titration
    """

    def __init__(self, target):
        self.endpoint = target
        TitrationWidget.__init__(self)

    def on_change(self, change):
        "Set concentration for target molecule."
        if self.validate(change['new']):
            self.set_value(change['new'])
        else:
            self.invalid_callback(change)
        self.change_callback()

    def invalid_callback(self, change):
        pass

    def set_value(self, value):
        setattr(self.titration, self.endpoint, value)

    def get_value(self):
        self.value = getattr(self.titration, self.endpoint)
        return self.value

    @staticmethod
    def validate(value):
        return True

    def change_callback(self):
        pass

class WidgetKwargs(object):
    widget_kw = {}

    @classmethod
    def update_kwargs(cls, kwargs):
        for key, value in cls.widget_kw.items():
            if key not in kwargs:
                kwargs.update({key:value})
        return kwargs


class TextControlWidget(AttrControlMixin, Text, WidgetKwargs):

    def __init__(self, target, *args, **kwargs):

        AttrControlMixin.__init__(self, target)
        type(self).update_kwargs(kwargs)
        Text.__init__(self, *args,**kwargs)
        self.value = self.get_value()


class FloatControlWidget(AttrControlMixin, BoundedFloatText, WidgetKwargs):
    widget_kw = {
        'min': 0,
        'max': 100000,
        "layout" : Layout(width='160px'),
        #'style' : {'description_width':'100px'}
    }

    def __init__(self, target, *args, **kwargs):
        AttrControlMixin.__init__(self, target)

        type(self).update_kwargs(kwargs)
        BoundedFloatText.__init__(self, *args,**kwargs)
        self.value = self.get_value()


class PanelContainer(VBox):

    HeaderBox = VBox
    ContentBox = VBox
    FooterBox = VBox

    def __init__(self, heading=[], content=[], footer=None, *args, **kwargs):
        VBox.__init__(self, *args, **kwargs)

        self.add_class('panel')
        self.add_class('panel-default')
        self.add_class('panel-shift2me')

        self.heading = self.HeaderBox(heading)
        self.content = self.ContentBox(content)
        self.footer = None

        if footer is not None:
            self.add_footer(footer)

        self.heading.add_class("panel-heading")
        self.content.add_class('panel-body')

        if self.footer:
            self.children = (self.heading, self.content, self.footer)
        else:
            self.children = (self.heading, self.content)


    def add_footer(self, widget_list=[]):
        self.footer=self.FooterBox(widget_list)
        self.footer.add_class('panel-footer')
        self.children = (self.heading, self.content, self.footer)

    def set_heading(self, widget_list):
        self.heading.children = widget_list

    def set_content(self, widget_list):
        self.content.children = widget_list

    def set_footer(self, widget_list):
        self.footer.children = widget_list


class NameWidget(TextControlWidget):
    "Sets study name"

    widget_kw = {
        'description' : 'Experiment name:',
        'style': {'description_width': '130px'},
    }

    def __init__(self, *args, **kwargs):
        TextControlWidget.__init__(self, 'name', *args, **kwargs)

    def on_change(self, change):
        self.titration.set_name(change['new'])

    def update(self):
        self.value = self.titration.name


class ConcentrationWidget(AttrControlMixin, BoundedFloatText, WidgetKwargs):
    """Sets concentration for one of the molecule

    molecule : str 'analyte', 'titrant'
    """

    widget_kw = {
        'min': 0,
        'max': 100000,
        "layout" : Layout(width='100px'),
        #'style' : {'description_width':'100px'}
    }

    def __init__(self, target, *args, **kwargs):
        kwargs.update({
            'value' : getattr(self.titration, target)['concentration'],
        })
        type(self).update_kwargs(kwargs)

        BoundedFloatText.__init__(self, *args, **kwargs)
        AttrControlMixin.__init__(self, target)

    def set_value(self, value):
        "Set concentration for target molecule."
        getattr(self.titration, self.endpoint)['concentration'] = value

    def get_value(self):
        self.value = getattr(self.titration, self.endpoint)['concentration']
        return self.value


class MoleculeNameWidget(AttrControlMixin, Text, WidgetKwargs):
    """Sets name for one of the molecule

    molecule : str 'analyte', 'titrant'
    """

    widget_kw = {
        "layout" : Layout(width='100px'),
        #'style' : {'description_width':'100px'}
    }

    def __init__(self, target, *args, **kwargs):
        assert target in ('analyte', 'titrant'), "Invalid argument {arg}: must be 'analyte' or 'titrant'"

        kwargs.update({
            'value': getattr(self.titration, target)['name'],
        })

        type(self).update_kwargs(kwargs)

        Text.__init__(self, *args, **kwargs)
        AttrControlMixin.__init__(self, target)

    def set_value(self, value):
        "Set name for target molecule."
        getattr(self.titration, self.endpoint)['name'] = value

    def get_value(self):
        self.value = getattr(self.titration, self.endpoint)['name']
        return self.value

class SingleMolContainer(TitrationWidget,VBox):
    # styles = {
    #     "label": ,
    #     "field":
    # }

    desc_kwargs = {
        'style': {'description_width': '130px'},
        'layout': Layout(width="230px")
    }

    def __init__(self, target, desc=False, *args, **kwargs):
        assert target in ('analyte', 'titrant'), "Invalid argument {arg}: must be 'analyte' or 'titrant'"

        VBox.__init__(self, *args, **kwargs)

        if desc:
            self.label = Label(value=target.title(), layout=Layout(left="150px"), justify_content="flex-end")
            self.name_field = MoleculeNameWidget(target, description = "Name:", **self.desc_kwargs)
            self.conc_field = ConcentrationWidget(target, description = "Concentration (µM):", **self.desc_kwargs)
        else:
            self.label = Label(value=target.title())
            self.name_field = MoleculeNameWidget(target)
            self.conc_field = ConcentrationWidget(target)


        self.children = (self.label, self.name_field, self.conc_field)

    def container_observe(self, func, name = 'value'):
        self.name_field.observe(func, name)
        self.conc_field.observe(func, name)

    def update(self):
        self.name_field.get_value()
        self.conc_field.get_value()

class MoleculesContainer(TitrationWidget, HBox):

    def __init__(self, *args,**kwargs):
        HBox.__init__(self, *args, **kwargs)
        TitrationWidget.__init__(self)

        # labels = VBox()
        # for label in ('', 'Name:', 'Concentration (µM):'):
        #     labels.children += (Label(label, width=120), )
        self.analyte = SingleMolContainer('analyte', desc=True)
        self.titrant = SingleMolContainer('titrant')
        self.children = (self.analyte, self.titrant)

    def container_observe(self, func, name='value'):
        self.analyte.container_observe(func, name)
        self.titrant.container_observe(func, name)

    def update(self):
        self.analyte.update()
        self.titrant.update()


class StartParamContainer(TitrationWidget, PanelContainer):

    layout_kw = {
        'style': {'description_width': '130px'},
        'layout': Layout(width="230px")
    }

    def __init__(self, *args, **kwargs):
        PanelContainer.__init__(self, layout=Layout(min_width='350px', width='68%'), *args, **kwargs)
        TitrationWidget.__init__(self)

        self.observers = set()

        # name_kw = dict(self.layout_kw)
        # name_kw['layout'] = Layout(width="335px")

        self.titrationName = NameWidget()
        self.titrationName.add_class('panel-header-title')

        self.analyteStartVol = FloatControlWidget(
            'analyteStartVol',
            description='Analyte volume (µL):',
            **self.layout_kw)
        self.startVol = FloatControlWidget(
            'startVol',
            description='Total volume (µL):',
            **self.layout_kw)

        self.molecules = MoleculesContainer()
        self.molecules.container_observe(self.on_change)

        self.titrationName.observe(self.on_change, 'value')

        self.analyteStartVol.observe(self.on_change, 'value')
        self.startVol.observe(self.on_change, 'value')

        self.set_heading([self.titrationName])
        self.set_content([self.molecules,self.analyteStartVol, self.startVol])

    def add_observer(self, obs):
        self.observers.add(obs)

    def on_change(self, change):
        for obs in self.observers:
            obs.update()

    def update(self):
        self.titrationName.update()
        self.analyteStartVol.get_value()
        self.startVol.get_value()
        self.molecules.update()


class VolumeWidget(TitrationWidget, BoundedFloatText, WidgetKwargs):

    widget_kw = {
        'min': 0,
        'max': 100000,
        "layout" : Layout(width='100%', height='28px'),
        'style' : {'description_width':'50%'}
    }

    def __init__(self, step_id, *args, **kwargs):
        self.step_id = int(step_id)
        type(self).update_kwargs(kwargs)
        kwargs['description'] = "Step {number:d}".format(number=self.step_id)
        BoundedFloatText.__init__(self, *args,**kwargs)
        TitrationWidget.__init__(self)


class ProtocolePanel(TitrationWidget, PanelContainer):

    def __init__(self, *args, **kwargs):
        self.title = Label('Protocole')
        self.title._dom_classes += ('panel-header-title',)

        PanelContainer.__init__(self, [self.title],  *args, **kwargs)
        TitrationWidget.__init__(self)

        self.update()

    def update(self):
        self.protocole = HTML(self.titration.make_protocole(index=False).to_html(index=False))
        self.protocole._dom_classes += ('rendered_html', 'protocole-table')
        self.set_content([self.protocole])


class VolumePanel(TitrationWidget, PanelContainer):

    def __init__(self, *args, **kwargs):
        PanelContainer.__init__(self, *args, **kwargs)
        TitrationWidget.__init__(self)

        self.steps = 0
        self._dom_classes += ('volumes-container',)

        self.add_button = Button(
            description = 'Add',
            button_style='primary',
            layout=Layout(width='50%'),
            icon="plus-circle")
        self.add_button.on_click(self.add_volume)

        self.remove_button = Button(
            description='Remove',
            button_style='warning',
            layout=Layout(width='50%'),
            disabled=True,
            icon="minus-circle")
        self.remove_button.on_click(self.remove_volume)

        self.buttons = HBox(
            [self.add_button, self.remove_button],
            layout=Layout(
                padding="5px 5px 5px 5px"))

        self.validate_button = Button(
            description='Validate',
            button_style='success',
            layout=Layout(width='100%'),
            disabled=False,
            icon='check')
        self.validate_button.on_click(self.send_volumes)

        self.volumesBox = VBox(
            [],
            layout=Layout(
                display='flex',
                flex_flow="column",
                padding='5px 5px 5px 5px'))

        formLabel = Label("Added titrant volumes")
        formLabel._dom_classes += ('panel-header-title',)

        self.set_heading([formLabel, self.buttons])
        self.set_content([self.volumesBox])
        self.add_footer([self.validate_button])

        self.volWidgets = []
        for volume in self.titration.volumes:
            self.add_volume()


    def update(self):
        self.steps = 0
        self.volWidgets = []
        for volume in self.titration.volumes:
            self.add_volume()
        self.update_children()

    def update_children(self):
        self.volumesBox.children = self.volWidgets
        self.set_content([self.volumesBox])
        # protocole = HTML(self.titration.make_protocole(index=False).to_html(index=False))

        # protocole._dom_classes += ('rendered_html', )
        # self.children = (
        #     self.form,
        #     protocole)

    def send_volumes(self, button):
        self.titration.set_volumes(self.volumes)
        self.update_children()

    def add_volume(self, button=None, disabled=False):
        if self.steps == 0:
            disabled = True
        else:
            self.remove_button.disabled = False

        if self.steps < self.titration.steps:
            value = self.titration.volumes[self.steps]
        else:
            value = 0
        self.volWidgets.append(
            VolumeWidget(self.steps, value=value, disabled=disabled)
        )

        self.update_children()
        self.steps += 1

    def remove_volume(self, button):
        if len(self.volWidgets) > 1:
            vol =  self.volWidgets.pop()
            del vol
            self.update_children()
            self.steps -= 1
        if self.steps <= 1:
            self.remove_button.disabled = True


    @property
    def volumes(self):
        return [widget.value for widget in self.volWidgets]


class ProtocoleContainer(HBox):

    def __init__(self, *args, **kwargs):
        HBox.__init__(self, *args, **kwargs, layout=Layout(justify_content='space-around'))

        self.volumes = VolumePanel(layout=Layout(width='30%', height="auto"))
        self.volumes.validate_button.on_click(self.on_submit)

        self.protocole = ProtocolePanel(layout=Layout(width='68%', height="auto"))

        self.children = (self.volumes, self.protocole)

    def on_submit(self, button):
        self.protocole.update()

    def update(self):
        self.volumes.update()
        self.protocole.update()

class TitrationDirUploader(TitrationWidget, DirectoryUploadWidget):

    def __init__(self, *args, **kwargs):
        DirectoryUploadWidget.__init__(self, *args, **kwargs)
        self.label = "Upload titration directory"
        self.output = Output()
        self.observers = set()
        self._dom_classes += ('upload-directory-btn',)

    def dispatch(self):
        for obs in self.observers:
            obs.update()

    def add_observer(self, obs):
        "Observer must have a update() method"
        self.observers.add(obs)

    @observe('files')
    def _files_changed(self, *args):
        if self.files:
            self.extract_chemshifts()
            self.extract_protocole()
            self.dispatch()

    @observe('base64_files')
    def _base64_files_changed(self, *args):
        for name, file in self.base64_files.items():
            self.files[name] = base64.b64decode(file.split(',',1)[1])
        self._files_changed(self, *args)

    def extract_chemshifts(self):
        filenames = set([file for file in self.files.keys() if file.endswith('.list')]) - set(self.titration.files)
        filenames = sorted(filenames, key=self.titration.validate_filepath)
        with self.output:
            for fname in filenames:
                Titration.add_step(self.titration, fname, io.StringIO(self.files[fname].decode('utf-8')))

    def extract_protocole(self):
        filenames = set([file for file in self.files.keys() if file.endswith('.yml')])
        with self.output:
            for fname in filenames:
                self.titration.load_init_file(io.StringIO(self.files[fname].decode('utf-8')))


class TitrationFilesView(TitrationWidget, PanelContainer ):
    def __init__(self, *args, **kwargs):

        PanelContainer.__init__(self, *args,**kwargs)

        self.add_class('data-files-view')

        self.label = Label("Data files")
        self.label.add_class('panel-header-title')
        self.layout.width="30%"
        self.content.layout.max_height="200px"
        self.content.layout.height="200px"
        self.content.layout.overflow_x="scroll"
        self.content.layout.overflow_y="scroll"
        self.content.layout.display="inline-block"
        self.set_heading([self.label])
        self.uploader = TitrationDirUploader()
        self.uploader.add_class('file-uploader')
        self.uploader.add_observer(self)
        self.add_footer([self.uploader])
        self.update()

    def update(self):
        self.files = self.titration.files
        if self.files:
            content = HTML(pd.DataFrame(data=self.files).to_html(index=False, header=False))
            content.add_class('rendered_html')

        else:
            content = Label('No files yet.')
        self.set_content([content])


