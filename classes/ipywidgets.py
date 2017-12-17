from ipywidgets import Box, HBox, VBox, BoundedFloatText, Button, Text, Widget, Label, Layout

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

class NameWidget(TextControlWidget):
    "Sets study name"

    widget_kw = {
        'description' : 'Titration name:'
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


# class ConcentrationLabelWidget(TitrationWidget, Label):
#     """Displays one molecule name
    
#     molecule : str 'analyte', 'titrant'
#     """
#     def __init__(self, target, name_widget, *args, **kwargs):
       
#         Label.__init__(self, *args, **kwargs)
#         self.set_value(getattr(self.titration, target)['name'])
#         name_widget.observe(self.update, names='value')
        
#     def update(self, change):
#         self.set_value(change['new'])

#     def set_value(self, value):
#         self.value = "[{label}] (µM)".format(label=value)


# class ConcentrationContainer(TitrationWidget, HBox):
#     style = {
#         'layout': Layout(width='120px', description_width='100px'),
#     }

#     def __init__(self, target, *args, **kwargs):
#         assert target in ('analyte', 'titrant'), "Invalid argument {arg}: must be 'analyte' or 'titrant'"

#         HBox.__init__(self, *args, **kwargs)
#         field = ConcentrationWidget(target, **self.field_kw)
#         label = ConcentrationLabelWidget(target, field)
#         self.children = (label, field)


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



class StartParamContainer(TitrationWidget, VBox):

    layout_kw = {
        'style': {'description_width': '130px'}, 
        'layout': Layout(width="230px")
    }

    def __init__(self, *args, **kwargs):
        VBox.__init__(self, *args, **kwargs)
        TitrationWidget.__init__(self)

        name_kw = dict(self.layout_kw)
        name_kw['layout'] = Layout(width="335px")
        titrationName = NameWidget(
            **name_kw)

        analyteStartVol = FloatControlWidget(
            'analyteStartVol', 
            description='Analyte volume (µL):', 
            **self.layout_kw)
        startVol = FloatControlWidget(
            'startVol', 
            description='Total volume (µL):', 
            **self.layout_kw)

        self.children = ( titrationName, MoleculesContainer(),analyteStartVol, startVol)


class VolumesContainer(TitrationWidget, VBox):

    def __init__(self, *args, **kwargs):
        VBox.__init__(self, *args, **kwargs)
        TitrationWidget.__init__(self)

