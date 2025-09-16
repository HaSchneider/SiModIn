from .. import interface as link
from tespy.networks import Network
from tespy.components import Source, Sink, PowerSource, PowerSink


def extract_technosphere_flows(SimModel: link.SimModel):
    '''
    Scans the Tespy network defined in the abstract method "init_model" and select all incoming and outcomin flows in the technosphere dict. 
    No functional unit is defined here!
    Power and massflow is transfered in energy and mass to be compatible with most lca datasets.

    Returns:
    Dict of the schema:
    technosphere= {'model_flow name': link.technosphere_flow }
    '''
    technosphere={}

    for comp in SimModel.model.comps['object']:
        
        if isinstance(comp, Sink):
            technosphere[comp.label]=link.technosphere_edge(
                name = comp.label,
                source=SimModel,
                target= None,
                amount = SinkAmount(SimModel.model, comp.label),#lambda model:comp,#(model.get_comp(comp.label).inl[0].m._val * model.units.ureg.hour).to('kg'),
                type= link.technosphereTypes.output)
        elif isinstance(comp, Source):
            technosphere[comp.label]=link.technosphere_edge(
                name = comp.label,
                source=None,
                target= SimModel,
                amount = SourceAmount(SimModel.model, comp.label),#lambda model:comp,#(model.get_comp(comp.label).outl[0].m._val* model.units.ureg.hour).to('kg'),
                type= link.technosphereTypes.input)
        elif isinstance(comp, PowerSink):
            technosphere[comp.label]=link.technosphere_edge(
                name = comp.label,
                source=SimModel,
                target= None,
                amount = PowerSinkAmount(SimModel.model, comp.label),#lambda model:(model.get_comp(comp.label).power_inl[0].E._val* model.units.ureg.hour).to('MJ'),
                type= link.technosphereTypes.output)
        elif isinstance(comp, PowerSource):
            technosphere[comp.label]=link.technosphere_edge(
                name = comp.label,
                source=None,
                target= SimModel,
                amount = PowerSourceAmount(SimModel.model, comp.label),
                type= link.technosphereTypes.input)
    return technosphere

class amount_container():
    def __init__(self, model,comp):
        self.comp = comp
        self.model = model
        
    def __call__(self):
        return self.value()
    
class PowerSourceAmount(amount_container):
    def value(self):
        return (self.model.get_comp(self.comp).power_outl[0].E._val* 
                       self.model.units.ureg.hour).to('MJ')

class PowerSinkAmount(amount_container):
    def value(self):
        return (self.model.get_comp(self.comp).power_inl[0].E._val* 
                       self.model.units.ureg.hour).to('MJ')
        
class SourceAmount(amount_container):
    def value(self):
        return (self.model.get_comp(self.comp).outl[0].m._val* 
                       self.model.units.ureg.hour).to('kg')

class SinkAmount(amount_container):
    def value(self):
        return (self.model.get_comp(self.comp).inl[0].m._val* 
                       self.model.units.ureg.hour).to('kg')