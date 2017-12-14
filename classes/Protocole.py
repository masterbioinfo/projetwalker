
class ProtocoleSteps(object):
    step_nb = 0
    style = {'description_width' : '200px'}
    layout = {"width" : '300px'}
    volume_layout = {"width" : '300px',"margin-top": '120px'}
    btn_layout = {"width" :'150', "margin-top": '20'}
    
    def __init__(self, titration = None):
        
        self.titration = titration
        
        # init volumes widgets
        self.volumesBox = VBox()
        self.volumeWidgets = []
        self.add_volume(disabled = True)
        
        # init concentration widgets
        self.initConcentration = []
        for label in ('[analyte] (µL)', '[titrant] (µL)'):
            widget = widgets.BoundedFloatText(
                value=0, 
                min=0,
                step=0.01,
                description=label, 
                style=self.style, 
                layout=self.layout,
                disabled=False
            )
            self.initConcentration.append(widget)
            
        # init start volumes widgets
        self.initVolumes = []
        for label in ('Analyte start volume', 'Total volume'):
            widget = widgets.BoundedFloatText(
                value=0, 
                min=0,
                step=0.01,
                description=label,
                style=self.style, 
                layout=self.volume_layout,
                disabled=False,
            )
            self.initVolumes.append(widget)
        
        # layout initial parameters
        volumeBox = VBox(self.initVolumes)
        concentrationBox = VBox(self.initConcentration)
        self.initBox = HBox([volumeBox, concentrationBox])
        
        
        
        self.btn = widgets.Button(description = 'Add', style=style, layout=self.btn_layout)
        self.btn.on_click(self.on_btn_clicked)
        
        
        
        #self.right_box = VBox([self.items[0], self.items[1],self.items[2], self.items[3]])
        #self.left_box = VBox([self.concentration_text,self.btn])
        
        self.mainBox = VBox([self.initBox, self.volumesBox, self.btn])
        
    @property
    def volumes(self):
        return [volWidget.value for volWidget in self.volumeWidgets]
        
    def on_btn_clicked(self,b):
        self.add_volume()

    def volume_changed(self, change):
        print("Vol Changed !")
        
    def add_volume(self, disabled=False):
        widget = widgets.BoundedFloatText(
            value=0, 
            min=0,
            step=0.01,
            description="Step {step}".format(step=self.step_nb), 
            style=self.style, 
            layout=self.layout,
            disabled=disabled
        )
        
        widget.observe(self.volume_changed, names='value')
        
        self.volumeWidgets.append(widget)
        self.volumesBox.children = self.volumeWidgets
        self.step_nb += 1

protocole = ProtocoleSteps()
display(protocole.mainBox)
