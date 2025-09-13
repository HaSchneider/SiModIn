from .. import interface as link
from tespy.networks import Network
from tespy.components import Source, Sink, PowerSource, PowerSink


def extract_technosphere_flows(SimModel: link.SimModel, model: Network):
    '''
    Scans the Tespy network defined in the abstract method "init_model" and select all incoming and outcomin flows in the technosphere dict. 
    No functional unit is defined here!
    Power and massflow is transfered in energy and mass to be compatible with most lca datasets.

    Returns:
    Dict of the schema:
    technosphere= {'model_flow name': link.technosphere_flow }
    '''
    technosphere={}

    for comp in model.comps['object']:
        
        if isinstance(comp, Sink):
            technosphere[comp.label]=link.technosphere_edge(
                name = comp.label,
                source=SimModel,
                target= None,
                amount = lambda:(comp.inl[0].m._val * model.units.ureg.hour).to('kg'),
                type= link.technosphereTypes.output)
        elif isinstance(comp, Source):
            technosphere[comp.label]=link.technosphere_edge(
                name = comp.label,
                source=None,
                target= SimModel,
                amount = lambda:(comp.outl[0].m._val* model.units.ureg.hour).to('kg'),
                type= link.technosphereTypes.input)
        elif isinstance(comp, PowerSink):
            technosphere[comp.label]=link.technosphere_edge(
                name = comp.label,
                source=SimModel,
                target= None,
                amount = lambda:(comp.power_inl[0].E._val* model.units.ureg.hour).to('MJ'),
                type= link.technosphereTypes.output)
        elif isinstance(comp, PowerSource):
            technosphere[comp.label]=link.technosphere_edge(
                name = comp.label,
                source=None,
                target= SimModel,
                amount = lambda:(comp.power_outl[0].E._val* model.units.ureg.hour).to('MJ'),
                type= link.technosphereTypes.input)
    return technosphere
