from .. import interface as link
from tespy.networks import Network
from tespy.components import Source, Sink, PowerSource, PowerSink


def extract_technosphere_flows(SimModel: link.SimModel, model: Network):
    '''
    Scans the Tespy network defined in the abstract method "init_model" and select all incoming and outcomin flows in the technosphere dict. 
    No functional unit is defined here!

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
                amount = SimModel.ureg.Quantity(comp.inl[0].m.val,
                                                comp.inl[0].m.unit) * SimModel.ureg.second,
                type= link.technosphereTypes.output)
        elif isinstance(comp, Source):
            technosphere[comp.label]=link.technosphere_edge(
                name = comp.label,
                source=None,
                target= SimModel,
                amount = SimModel.ureg.Quantity(comp.outl[0].m.val,
                                                comp.outl[0].m.unit)* SimModel.ureg.second,
                type= link.technosphereTypes.input)
        elif isinstance(comp, PowerSink):
            technosphere[comp.label]=link.technosphere_edge(
                name = comp.label,
                source=SimModel,
                target= None,
                amount = SimModel.ureg.Quantity(comp.power_inl[0].E.val,
                                                comp.power_inl[0].E.unit) * SimModel.ureg.second,
                type= link.technosphereTypes.output)
        elif isinstance(comp, PowerSource):
            technosphere[comp.label]=link.technosphere_edge(
                name = comp.label,
                source=None,
                target= SimModel,
                amount = SimModel.ureg.Quantity(comp.power_outl[0].E.val,
                                                comp.power_outl[0].E.unit)* SimModel.ureg.second,
                type= link.technosphereTypes.input)
    return technosphere
