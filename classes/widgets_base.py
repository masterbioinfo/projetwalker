from ipywidgets import *
from traitlets import observe

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
