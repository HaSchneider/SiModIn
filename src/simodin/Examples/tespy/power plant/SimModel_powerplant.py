from simodin import interface as link
import model
from simodin import tespy 

class tespy_model(link.SimModel):
    def init_model(self,  **params):
        self.model = model.create_network()

    def calculate_model(self):
        self.model.solve("design")
        self.model.get_comp('condenser').set_attr(ttd_u=5)
        self.model.get_conn('6').set_attr(p=None)
        self.model.solve("design")

    def recalculate_model(self, **model_params):
        return super().recalculate_model(**model_params)
    
    @property
    def technosphere(self):
        #get all technosphere flows:
        technosphere=tespy.extract_technosphere_flows(self, self.model)
        #set functional unit:
        technosphere['grid'].functional = True
        return technosphere
        
    @property
    def biosphere(self) -> dict:
        return {}
    