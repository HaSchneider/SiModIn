from .. import interface as link
#import pythoncom
#pythoncom.CoInitialize()


def extract_dwsim_flows(SimModel: link.SimModel, model):
    '''
    Scans the DESIM flowsheet defined in the abstract method "init_model" and select all incoming and outgoing flows in the technosphere dict. 
    No functional unit is defined here, and all flows are stored in technosphere dictionary. 
    Power and massflow is transfered in energy and mass to be compatible with most lca datasets.

    Returns:
    Dict of the schema:
    technosphere= {'model_flow name': link.technosphere_flow }
    '''
    

    technosphere={}

    for obj in model.SimulationObjects.values():
        obj= obj.GetAsObject()
        # check for incoming and outgoing material streams:
        if isinstance(obj, SimModel.DWSIM.Thermodynamics.Streams.MaterialStream):
            if obj.GetConnectionPortsInfo()[1].IsConnected and not obj.GetConnectionPortsInfo()[0].IsConnected: # inlet stream
                technosphere[f'{obj.GetDisplayName()} - {obj.Name}']=link.technosphere_edge(
                    name = f'{obj.GetDisplayName()} - {obj.Name}',
                    source=None,
                    target= SimModel,
                    amount = lambda:(SimModel.ureg.Quantity(obj.GetMassFlow() , obj.GetPropertyUnit('PROP_MS_2'))* SimModel.ureg.second),
                    type= link.technosphereTypes.output)
        elif isinstance(obj, SimModel.DWSIM.Thermodynamics.Streams.MaterialStream):
            if obj.GetConnectionPortsInfo()[0].IsConnected and not obj.GetConnectionPortsInfo()[1].IsConnected: # outlet stream
                technosphere[f'{obj.GetDisplayName()} - {obj.Name}']=link.technosphere_edge(
                    name = f'{obj.GetDisplayName()} - {obj.Name}',
                    source=SimModel,
                    target= None,
                    amount = lambda:(SimModel.ureg.Quantity(obj.GetMassFlow() , obj.GetPropertyUnit('PROP_MS_2'))* SimModel.ureg.second),
                    type= link.technosphereTypes.input)
        
        elif isinstance(obj, SimModel.DWSIM.UnitOperations.Streams.EnergyStream):
            if obj.GetConnectionPortsInfo()[1].IsConnected and not obj.GetConnectionPortsInfo()[0].IsConnected: # inlet stream
                technosphere[f'{obj.GetDisplayName()} - {obj.Name}']=link.technosphere_edge(
                    name = f'{obj.GetDisplayName()} - {obj.Name}',
                    source=None,
                    target= SimModel,
                    amount = lambda:( SimModel.ureg.Quantity(obj.GetMassFlow() , obj.GetPropertyUnit('PROP_ES_0'))* SimModel.ureg.second),
                    type= link.technosphereTypes.output)
        elif isinstance(obj, SimModel.DWSIM.UnitOperations.Streams.EnergyStream):
            if obj.GetConnectionPortsInfo()[0].IsConnected and not obj.GetConnectionPortsInfo()[1].IsConnected: # outlet stream
                technosphere[f'{obj.GetDisplayName()} - {obj.Name}']=link.technosphere_edge(
                    name = f'{obj.GetDisplayName()} - {obj.Name}',
                    source=SimModel,
                    target= None,
                    amount = lambda:(SimModel.ureg.Quantity(obj.GetMassFlow() , obj.GetPropertyUnit('PROP_ES_0'))* SimModel.ureg.second),
                    type= link.technosphereTypes.input)
    return technosphere
