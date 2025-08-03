import bw2data as bd
import bw2calc as bc
from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict, Field, JsonValue
from typing import Dict, Union, Optional,Callable, Literal
import datetime
import pint
import warnings
from enum import StrEnum

class SimModel(ABC):
    """Class containing a simulation model.

    Args:
        **model_params: Parameters for the simulation Model.
    
    """
    def __init__(self, name, **model_params):
        self.name = name
        self.ureg=pint.UnitRegistry()
        self.params= model_params
        self.location = 'GLO'
    
    @abstractmethod
    def init_model(self, **model_params):
        '''Abstract method to initiate the model.

        Args:
            **model_params: Parameters for the simulation Model. 
        '''
        
        self.params= self.params|model_params

    @abstractmethod
    def calculate_model(self, **model_params):
        '''Abstract method to calculate the model based on the parameters provided.
        '''
        pass

    @abstractmethod
    def recalculate_model(self, **model_params):
        '''Abstract method to recalculate the model based on the parameters provided.
        '''
        pass
    
    @property
    @abstractmethod
    def technosphere(self):
        '''Abstract property to define the model technosphere flows. 
        Creates a dict of technosphere flows, wich nedds to be filled by the modelInterface class with brightway datasets.

        Dict of the schema: 
            {'model_flow name': simodin.interface.technosphere_edge }
        '''
        return {}
    
    @property
    @abstractmethod    
    def biosphere(self) -> dict:
        '''
        Abstract property to define the model biosphere flows. 
        
        Dict of the schema:
            {'model_flow name': simodin.interface.biosphere_edge }
        '''
        return {}
    
    def get_technosphere(self):
        '''
        TODO might be unncessary as abstract property works as a getter function.
        Method to get the current technosphere dict. 
        Needs to be executed when the model gets recalculated and no callable objects are used.
        
        '''
        return self.technosphere

# pydantic schema adapted from bw_interface_schemas: 
# https://github.com/brightway-lca/bw_interface_schemas
class QuantitativeEdgeTypes(StrEnum):
    technosphere = "technosphere"
    biosphere = "biosphere"
    characterization = "characterization"
    weighting = "weighting"
    normalization = "normalization"
    
class technosphereTypes(StrEnum):
    product= "product"
    substitution= "substitution"
    input= "input"
    output= "output"

class Edge(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    edge_type: str
    source: bd.backends.proxies.Activity | SimModel|None = None
    target: bd.backends.proxies.Activity | SimModel|None = None
    comment: Union[str, dict[str, str], None] = None
    tags: dict[str, JsonValue] | None = None
    properties: dict[str, JsonValue] | None = None
    name: str

class QuantitativeEdge(Edge):
    """An quantitative edge linking two nodes in the graph."""

    edge_type: QuantitativeEdgeTypes
    amount: Union[pint.Quantity, float,Callable]
    uncertainty_type: int | None = None
    loc: float | None = None
    scale: float | None = None
    shape: float | None = None
    minimum: float | None = None
    maximum: float | None = None
    negative: bool | None = None
    description: Union[str, dict[str, str], None] = None
    dataset_correction: float | None = None

class technosphere_edge(QuantitativeEdge):
    """A technosphere flow."""
    functional: bool = False
    edge_type: Literal[QuantitativeEdgeTypes.technosphere] = (
        QuantitativeEdgeTypes.technosphere
    )
    model_unit: Union[pint.Unit, str, None] =None
    dataset_unit: Union[pint.Unit, str, None] =None
    allocationfactor: float= 1.0
    type: technosphereTypes

class biosphere_edge(QuantitativeEdge):
    """A biosphere flow."""
    edge_type: Literal[QuantitativeEdgeTypes.biosphere] = (
        QuantitativeEdgeTypes.biosphere
    )
    model_unit: Union[pint.Unit, str, None] =None
    dataset_unit: Union[pint.Unit, str, None] =None


class modelInterface(BaseModel):
    '''Class for interface external activity models with brightway25.
    
    Attributes:
    ----------
        name: Name of the model.
        model: The Simulation model.
    
    
    '''
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    model: SimModel
    name: str

    technosphere: Dict[str, technosphere_edge]={}
    biosphere: Dict[str, biosphere_edge]={}
    params: Optional[Dict[str, Union[float, int, bool, str]]]=None
    methods: list=[]
    converged: bool= False
    ureg: pint.UnitRegistry=pint.UnitRegistry()
    method_config: Dict={}
    impact_allocated: Dict={}
    impact: dict={}
    lca: Optional[bc.MultiLCA]=None

    def __init__(self, name, model):
        super().__init__(name=name, model=model)
        #self.name = name
        self.technosphere= self.model.technosphere
        self.biosphere= self.model.biosphere
        self.params = self.model.params
        self.ureg = self.model.ureg

    def update_flows(self):
        for name,flow   in self.technosphere.items():
            flow.amount = self.model.technosphere[name].amount

    def setup_link(self):

        self.technosphere= self.model.technosphere
        self.biosphere= self.model.biosphere

    def calculate_background_impact(self):
        '''
        Calculate the background impact based on the parameters provided.
        '''
        if self.technosphere is None:
            raise ValueError("technosphere dict not created. Define and call 'link_technosphere' first.")
        
        background_flows={}
        for name, ex in self.technosphere.items():
            if ex.functional:
               continue 
            if ex.source == self.model:
                if isinstance(ex.target, bd.backends.proxies.Activity):
                    background_flows[name]= {ex.target.id:1}    
            else:
                if isinstance(ex.source, bd.backends.proxies.Activity):
                    background_flows[name]= {ex.source.id:1}

        self.method_config= {'impact_categories':self.methods}
        if len(background_flows)==0:
             raise ValueError("Technosphere dict got no technosphere flows with an assigned brightway25 activity. LCA calculation abborted.")
        data_objs = bd.get_multilca_data_objs(background_flows, self.method_config)
        self.lca = bc.MultiLCA(demands=background_flows,
                    method_config=self.method_config, 
                    data_objs=data_objs
                    )
        self.lca.lci()
        self.lca.lcia()
    
    def calculate_impact(self):
        '''Calculate the impact and returns the allocated impact.

        '''
        if not hasattr(self, 'lca'):
            self.calculate_background_impact()
        self.impact_allocated = {}
        self.impact = {}
        for cat in self.method_config['impact_categories']:
            self.impact[cat] = 0
            for name, ex  in self.technosphere.items():
                
                if ex.functional:
                    continue
                #check if technosphere is linked to a bw activity
                if not isinstance(ex.target, bd.backends.proxies.Activity) and ex.source == self.model:
                    continue
                if not isinstance(ex.source, bd.backends.proxies.Activity) and ex.target == self.model:
                    continue
                score=self.lca.scores[(cat, name)]*self._get_flow_value(ex)
                
                if ex.dataset_correction != None:
                    score*= ex.dataset_correction  
                self.impact[cat] += score
            for name, ex in self.biosphere.items():
                cf_list=bd.Method(cat).load()
                if ex.source == self.model:
                    factor= [flow for flow in cf_list if flow[0]== ex.target.id][0][1]
                
                if ex.target== self.model:
                    factor= [flow for flow in cf_list if flow[0]== ex.source.id][0][1]

                self.impact[cat] += self._get_flow_value(ex)*factor

            self.impact_allocated[cat]={}
            #if isinstance(self.functional_unit, dict):
            for name, ex in self.technosphere.items():
                if not ex.functional:
                    continue
                else:
                    self.impact_allocated[cat][name] =(
                        self.impact[cat] * 
                        ex.allocationfactor/self._get_flow_value(ex)
                        )
        return self.impact_allocated
    
    def _get_flow_value(self, ex):
        '''Get the correct amount value and transform to the correct unit if possible.

        Args:
            ex: Exchange flow
        
        Returns:
            Amount: Amount as float.
          
        '''
        if callable(ex.amount):
            amount=ex.amount()
        else:
            amount= ex.amount
        # check for unit and transform it in the correct unit if possible.
        #get dataset unit:
        if  ex.target!= None:
            if ex.dataset_unit != None:
                dataset_unit= ex.dataset_unit
            elif ex.target == self.model and 'unit' in ex.source:
                dataset_unit=ex.source.get('unit')
            elif ex.source == self.model and 'unit' in ex.target:
                dataset_unit=ex.target.get('unit')
            else:
                raise ValueError(f'No dataset unit available for {ex.name}.')
        else:
            dataset_unit= 'NaU'
        #get model flow unit:
        if isinstance(amount, pint.Quantity) and dataset_unit in self.model.ureg:
            return amount.m_as(dataset_unit)
        elif isinstance(amount, pint.Quantity) and dataset_unit not in self.model.ureg:
            if dataset_unit != ' ':
                warnings.warn(f"The dataset of {ex.name} got no valid Pint Unit. Ignore unit transformation.", UserWarning)
            return amount.m
        # if no pint quantity                
        elif ex.model_unit!=None and ex.model_unit in self.model.ureg:
            if  ex.target!= None:
                if ex.target == self.model:
                    return self.model.ureg.Quantity(amount, ex.model_unit).m_as(ex.source.get('unit'))
                elif ex.source ==self.model:
                    return self.model.ureg.Quantity(amount, ex.model_unit).m_as(ex.target.get('unit'))
                elif ex.type =='product':
                    return amount
            else:
                return amount
        elif ex.model_unit!=None and ex.model_unit not in self.model.ureg:
            warnings.warn(f"The model flow  of {ex.name} got no valid Pint Unit. Ignore unit transformation.", UserWarning)
            return amount
        else:
            warnings.warn('No unit check possible for {ex.name}. Use pint units if possible or provide pint compatible model unit name.',UserWarning)
            return amount

    def export_to_bw(self, database=None, identifier=None):
        '''Export the model to a brightway dataset.
        Creates the database simulation_model_db if no database is passed. Creates a identifier by the model name, functional unit flow name, and a time stamp if none is passed.

        Args:
            database: Database in which the model activity should be exported.
            identifier: code for the brightway activity
        
        '''
        if not hasattr(self, 'impact_allocated'):
            self.calculate_impact()

        if database== None:
            database = f"simulation_model_db" 

        if database not in bd.databases:
            bd.Database(database).register() 
        
        for fun_name, fun_ex in self.technosphere.items():
            if not fun_ex.functional:
                continue
            now= datetime.datetime.now()
            if identifier==None:
                code= f'{self.name}_{fun_name}_{now}'

            else:
                code= f'{fun_name}_{identifier}'
            node = bd.Database(database).new_node(
                name= fun_name,
                unit= fun_ex.model_unit,
                code= code,
                **self.model.params
            )
            node.save()

            for name, ex in self.technosphere.items():
                if ex.functional:
                    continue
                #check if technosphere is linked to a bw activity
                if not isinstance(ex.target, bd.backends.proxies.Activity) and ex.source == self.model:
                    continue
                if not isinstance(ex.source, bd.backends.proxies.Activity) and ex.target == self.model:
                    continue
                
                allocated_amount= (self._get_flow_value(ex)*fun_ex.allocationfactor / 
                                    self._get_flow_value(fun_ex))
                #dataset correction for original linked dataset.
                if ex.dataset_correction != None:
                    allocated_amount= allocated_amount*ex.dataset_correction
                if ex.target == self.model:
                    node.new_exchange(
                        input= ex.source,
                        amount=allocated_amount,
                        type = 'technosphere',
                    ).save()
                elif ex.source == self.model:
                    node.new_exchange(
                        input= ex.target,
                        amount=allocated_amount,
                        type = 'technosphere',
                    ).save()

            for name, ex in self.biosphere.items():
                
                allocated_amount= (self._get_flow_value(ex)*fun_ex.allocationfactor / 
                                    self._get_flow_value(fun_ex))
                if ex.target == self.model:
                    node.new_exchange(
                        input= ex.source,
                        amount=allocated_amount,
                        type = 'biosphere',
                    ).save()
                elif ex.source == self.model:
                    node.new_exchange(
                        input= ex.target,
                        amount=allocated_amount,
                        type = 'biosphere',
                    ).save()            
            node.new_exchange(
                input=node,
                amount= 1,
                type = 'production',
            ).save()
        
        return code
    
