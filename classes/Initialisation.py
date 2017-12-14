class Initiation(object):
    
    def __init__(self):
        
        titration = None
        
        self.try_name =  widgets.Text(
            placeholder='Enter Experience Name',
            description='Experience name', 
            value="",
            disabled=False
        )
        
        self.pdbCode = widgets.Text(
            placeholder='Enter PDB code, exemple: 4wk4',
            description='PDB code',
            value="",
            disabled=False
        )
        self.seq_area = widgets.Textarea(
            value= '', 
            placeholder='Protein Sequence', 
            description='', 
            disabled=False, 
            display='flex', 
            flex_flow='row', 
            height='1000px'
        )
        
        #PDB and Seq Box
        
        pdb_seq_box = VBox([self.pdbCode, self.seq_area])
        
        # HBox : Experience name and Pdb and Seq Box
        
        self.hbox = HBox ([self.try_name, pdb_seq_box])

        
        

initiation = Initiation()

display(initiation.hbox)

