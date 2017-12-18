from ipywidgets import Box, HBox, VBox, BoundedFloatText, Button, Text, Widget, Label, Layout, HTML, Output
from ipyfileupload.widgets import DirectoryUploadWidget
from traitlets import observe
import base64, io

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

    def invalid_callback(self, change):
        pass

    def set_value(self, value):
        setattr(self.titration, self.endpoint, value)

    def get_value(self):
        return getattr(self.titration, self.endpoint)

    @staticmethod
    def validate(value):
        return True

class WidgetKwargs(object):
    widget_kw = {}

    @classmethod
    def update(cls, kwargs):
        for key, value in cls.widget_kw.items():
            if key not in kwargs:
                kwargs.update({key:value})
        return kwargs


class TextControlWidget(AttrControlMixin, Text, WidgetKwargs):

    def __init__(self, target, *args, **kwargs):

        AttrControlMixin.__init__(self, target)
        type(self).update(kwargs)
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

        type(self).update(kwargs)
        BoundedFloatText.__init__(self, *args,**kwargs)
        self.value = self.get_value()


class PanelContainer(VBox):

    HeaderBox = VBox
    ContentBox = VBox
    FooterBox = VBox

    def __init__(self, heading=[], content=[], footer=None, *args, **kwargs):
        VBox.__init__(self, *args, **kwargs)

        self._dom_classes += ('panel', 'panel-default')

        self.heading = self.HeaderBox(heading)
        self.content = self.ContentBox(content)
        self.footer = None

        if footer is not None:
            self.add_footer(footer)

        self.heading._dom_classes += ("panel-heading",)
        self.content._dom_classes += ('panel-body',)

        if self.footer:
            self.children = (self.heading, self.content, self.footer)
        else:
            self.children = (self.heading, self.content)


    def add_footer(self, widget_list=[]):
        self.footer=self.FooterBox(widget_list)
        self.footer._dom_classes += ('panel-footer',)
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
        'description' : 'Experiment name:'
    }

    def __init__(self, *args, **kwargs):
        TextControlWidget.__init__(self, 'name', *args, **kwargs)

    def on_change(self, change):
        self.titration.set_name(change['new'])


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
        type(self).update(kwargs)

        BoundedFloatText.__init__(self, *args, **kwargs)
        AttrControlMixin.__init__(self, target)
        
    def set_value(self, value):
        "Set concentration for target molecule."
        getattr(self.titration, self.endpoint)['concentration'] = value


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

        type(self).update(kwargs)

        Text.__init__(self, *args, **kwargs)
        AttrControlMixin.__init__(self, target)

    def set_value(self, value):
        "Set name for target molecule."
        getattr(self.titration, self.endpoint)['name'] = value

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
            label = Label(value=target.title(), layout=Layout(left="150px"), justify_content="flex-end")
            name_field = MoleculeNameWidget(target, description = "Name:", **self.desc_kwargs)
            conc_field = ConcentrationWidget(target, description = "Concentration (µM):", **self.desc_kwargs)
        else:
            label = Label(value=target.title())
            name_field = MoleculeNameWidget(target)
            conc_field = ConcentrationWidget(target)
        self.children = (label, name_field, conc_field)


class MoleculesContainer(TitrationWidget, HBox):

    def __init__(self, *args,**kwargs):
        HBox.__init__(self, *args, **kwargs)
        TitrationWidget.__init__(self)

        # labels = VBox()
        # for label in ('', 'Name:', 'Concentration (µM):'):
        #     labels.children += (Label(label, width=120), )
        analyte = SingleMolContainer('analyte', desc=True)
        titrant = SingleMolContainer('titrant')
        self.children = (analyte, titrant)




class StartParamContainer(TitrationWidget, PanelContainer):

    layout_kw = {
        'style': {'description_width': '130px'}, 
        'layout': Layout(width="230px")
    }

    def __init__(self, *args, **kwargs):
        PanelContainer.__init__(self, layout=Layout(width='400px'), *args, **kwargs)
        TitrationWidget.__init__(self)
        name_kw = dict(self.layout_kw)
        name_kw['layout'] = Layout(width="335px")
        
        titrationName = NameWidget(**name_kw)
        titrationName.add_class('panel-header-title')

        analyteStartVol = FloatControlWidget(
            'analyteStartVol', 
            description='Analyte volume (µL):', 
            **self.layout_kw)
        startVol = FloatControlWidget(
            'startVol', 
            description='Total volume (µL):', 
            **self.layout_kw)

        titrationName.observe(self.on_change, 'value')
        
        analyteStartVol.observe(self.on_change, 'value')
        startVol.observe(self.on_change, 'value')

        self.set_heading([titrationName])
        self.set_content([MoleculesContainer(),analyteStartVol, startVol])



class VolumeWidget(TitrationWidget, BoundedFloatText, WidgetKwargs):

    widget_kw = {
        'min': 0,
        'max': 100000,
        "layout" : Layout(width='100%', height='28px'),
        'style' : {'description_width':'50%'}
    }

    def __init__(self, step_id, *args, **kwargs):
        self.step_id = int(step_id)
        type(self).update(kwargs)
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
        self.volumes = VolumePanel(layout=Layout(width='250px', height="auto"))
        self.volumes.validate_button.on_click(self.on_submit)
        self.protocole = ProtocolePanel()
        self.children = (self.volumes, self.protocole)

    def on_submit(self, button):
        self.protocole.update()



class TitrationDirUploader(TitrationWidget, DirectoryUploadWidget, Button):

    def __init__(self, *args, **kwargs):
        DirectoryUploadWidget.__init__(self, *args, **kwargs)
        self.label = "Upload titration directory..."
        self.output = Output()
    @observe('files')
    def _files_changed(self, *args):
        if self.files:
            self.extract_chemshifts()  
            self.extract_protocole()
    
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
        self.label = Label("Data files")
        self.label._dom_classes += ('panel-header-title',)
        self.layout.width="200px"
        self.set_heading([self.label])
        self.update()

    def update(self):
        self.files = [Label(fname) for fname in self.titration.files]
        self.set_content(self.files)