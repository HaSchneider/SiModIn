import bw2data as bd
import bw2calc as bc
from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict, Field, JsonValue
from typing import Dict, Union, Optional,Callable, Literal
import datetime
import pint
import warnings
from enum import StrEnum
from functools import wraps
import functools
import pandas as pd


def update_params(func):
    """Decorator for overwrite params before call of concrete methods. 
    """
    @functools.wraps(func)
    def wrapper(self, **model_params):
        self.params =self.params | model_params 
        return func(self, **model_params)
    return wrapper


class SimModel(ABC):
    """Class containing a simulation model.

    Args:
        name: model name.
        init_arg: Arguments needed for initialising the model. 
        **model_params: Parameters for the simulation Model.
    
    """
    reference={ 
        'type': 'misc',
        'key': '',
        'author' :'',
        'title'  : '',
        'license': '',
        'url': ''
        }
    # Description of the model:
    description=''

    def __init__(self, name, init_arg=None, **model_params):
        super().__init__()
        self.name = name
        self.ureg=pint.UnitRegistry()
        self.params= model_params
        self.location = 'GLO'
        #self.init_model(init_arg, **model_params)
        #self.define_flows()
        self.converges= False

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if 'init_model' in cls.__dict__:
            cls.init_model = update_params(cls.init_model)
        if 'calculate_model' in cls.__dict__:
            cls.calculate_model = update_params(cls.calculate_model)
        if 'recalculate_model' in cls.__dict__:
            cls.recalculate_model = update_params(cls.recalculate_model)


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

    def recalculate_model(self, **model_params):
        '''Method to recalculate the model based on the parameters provided. 
        Executes a new initialising and calculation of the model. Might be 
        overwritten if a better and faster way to recalculate the model is possible.
        '''
        self.init_model(**model_params)
        self.calculate_model(**model_params)

    @property
    def technosphere(self):
        '''Property of the model technosphere flows. 
        A dict of technosphere flows, wich needs to be filled by the modelInterface class with brightway datasets.

        Dict of the schema: 
            {'model_flow name': simodin.interface.technosphere_edge }
        '''

        return self._technosphere
    
    @technosphere.setter
    def technosphere(self, technosphere_dict):
        '''
        Setter to define the model technosphere flows.
        '''
        self._technosphere= technosphere_dict
    
    @technosphere.getter
    def technosphere(self):
        data={
            "description":[],
            "amount":[],
            "functional":[],
            "dataset_correction":[],
            "reference":[],
            "allocationfactor":[],
            "model_unit":[],
            "impact":[],
            "source":[],
            "target":[],
            }
        for k, v in self._technosphere.items():
            for key, val in data.items():
                if key =='amount':
                    val.append(getattr(v, key)())   
                else:
                    val.append(getattr(v, key))
        df = pd.DataFrame(data, index = self._technosphere.keys())
        return(df)
    
    def print_technosphere(self, prop_list):
        data= {arg:[] for arg in prop_list }
        for k, v in self._technosphere.items():
            for key, val in data.items():
                if key =='amount':
                    val.append(getattr(v, key)())
                else:
                    val.append(getattr(v, key))
        df = pd.DataFrame(data, index = self._technosphere.keys())
        return(df)

    @property
    def biosphere(self) -> dict:
        '''
        Property of the model biosphere flows. 
        
        Dict of the schema:
            {'model_flow name': simodin.interface.biosphere_edge }
        '''
        return self._biosphere
    
    @biosphere.setter
    def biosphere(self, biosphere_dict): 
        '''
        Setter to define the model biosphere flows. 
        
        Dict of the schema:
            {'model_flow name': simodin.interface.biosphere_edge }
        '''
        self._biosphere= biosphere_dict
    
    @biosphere.getter
    def biosphere(self):
        data={
            "description":[],
            "amount":[],
            "source":[],
            "target":[],
            "dataset_correction":[],
            }
        for k, v in self._biosphere.items():
            for key, val in data.items():
                if key =='amount':
                    val.append(getattr(v, key)())   
                else:
                    val.append(getattr(v, key))
        df = pd.DataFrame(data, index = self._biosphere.keys())
        return(df)
    
    @abstractmethod
    def define_flows(self):
        '''Abstract method to define the model flows.
    
        '''
        pass

    def set_flow_attr(self, flow_name, flow_property, value):
        '''Set a property of a flow.

        Args:
            flow_name: Name of the flow to be set.
            flow_property: Property of the flow to be set.
            value: Value to be set.
        
        '''
        if flow_name in self._technosphere:
            if hasattr(self._technosphere[flow_name], flow_property):
                setattr(self._technosphere[flow_name], flow_property, value)
            else:
                raise ValueError(f'Flow property {flow_property} not found in technosphere flow {flow_name}.')
        elif flow_name in self._biosphere:
            if hasattr(self._biosphere[flow_name], flow_property):
                setattr(self._biosphere[flow_name], flow_property, value)
            else:
                raise ValueError(f'Flow property {flow_property} not found in biosphere flow {flow_name}.')
        else:
            raise ValueError(f'Flow {flow_name} not found in technosphere or biosphere.')
    
    def add_flow(self, flow: Union['technosphere_edge', 'biosphere_edge']):
        '''Add a flow to the flow dicts.

        Args:
            flow: Flow to be added.
        
        '''
        if isinstance(flow, technosphere_edge):
            if not hasattr(self, '_technosphere'):
                self._technosphere= {}
            self._technosphere[flow.name]= flow
        elif isinstance(flow, biosphere_edge):
            if not hasattr(self, '_biosphere'):
                self._biosphere= {}
            self._biosphere[flow.name]= flow
        else:
            raise ValueError(f'Flow {flow} is not a valid technosphere or biosphere flow.')
        
    @property
    def citation(self):
        '''Citation of the model:
        
        '''
        

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
    amount: Callable # Union[pint.Quantity, float,Callable]
    uncertainty_type: int | None = None
    loc: float | None = None
    scale: float | None = None
    shape: float | None = None
    minimum: float | None = None
    maximum: float | None = None
    negative: bool | None = None
    description: Union[str, dict[str, str], None] = None
    default_name: str = ''
    default_code: str = ''
    dataset_correction: float | None = None

class technosphere_edge(QuantitativeEdge):
    """A technosphere flow."""
    functional: bool = False
    reference: bool = False
    edge_type: Literal[QuantitativeEdgeTypes.technosphere] = (
        QuantitativeEdgeTypes.technosphere
    )
    model_unit: Union[pint.Unit, str, None] =None
    dataset_unit: Union[pint.Unit, str, None] =None
    allocationfactor: Union[float, Callable] =1.0
    type: technosphereTypes
    database: Union[str, None]=None
    dataset: Union[str, None]=None
    impact: Union[dict[str,Union[pint.Quantity, float]], None]=None 

class biosphere_edge(QuantitativeEdge):
    """A biosphere flow."""
    edge_type: Literal[QuantitativeEdgeTypes.biosphere] = (
        QuantitativeEdgeTypes.biosphere
    )
    model_unit: Union[pint.Unit, str, None] =None
    dataset_unit: Union[pint.Unit, str, None] =None


class modelInterface(BaseModel):
    '''Class for interface external simulation models with brightway25.
    
    Attributes:
    ----------
        name: Name of the model.
        model: The Simulation model as SimModel class.
    
    
    '''
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    model: SimModel
    name: str

    params: Optional[Dict[str, Union[float, int, bool, str]]]=None
    methods: list=[]
    converged: bool= False
    ureg: pint.UnitRegistry=pint.UnitRegistry()
    method_config: Dict={}
    impact_allocated: Dict={}
    impact_dissag: Dict={}
    impact: dict={}
    lca: Optional[bc.MultiLCA]=None
    _reference_flow: str=''

    def __init__(self, name, model):
        super().__init__(name=name, model=model)
        self.params = self.model.params
        self.ureg = self.model.ureg


    def add_dataset(self, flow_name, dataset):
        '''Link a brightway25 dataset to a model flow.

        Args:
            flow_name: Name of the flow to be linked.
            dataset: Brightway25 dataset to be linked.
        
        '''
        if flow_name in self.model._technosphere:
            if not isinstance(dataset, bd.backends.proxies.Activity):
                raise ValueError(f'Dataset {dataset} is not a valid brightway25 activity.')
            if self.model._technosphere[flow_name].target == self.model:
                self.model._technosphere[flow_name].source= dataset
            elif self.model._technosphere[flow_name].source == self.model:
                self.model._technosphere[flow_name].target= dataset
            
        elif flow_name in self.model._biosphere:
            if not isinstance(dataset, bd.backends.proxies.Activity):
                raise ValueError(f'Dataset {dataset} is not a valid brightway25 biosphere exchange.')
            if self.model._biosphere[flow_name].target == self.model:
                self.model._biosphere[flow_name].source= dataset
            elif self.model._biosphere[flow_name].source == self.model:
                self.model._biosphere[flow_name].target= dataset
            
        else:
            raise ValueError(f'Flow {flow_name} not found in technosphere or biosphere.')
        
    def remove_dataset(self, flow_name):
        if flow_name in self.model._technosphere:
            if self.model._technosphere[flow_name].target == self.model:
                self.model._technosphere[flow_name].source= None
            elif self.model._technosphere[flow_name].source == self.model:
                self.model._technosphere[flow_name].target= None
            
        elif flow_name in self.model._biosphere:
            if self.model._biosphere[flow_name].target == self.model:
                self.model._biosphere[flow_name].source= None
            elif self.model._biosphere[flow_name].source == self.model:
                self.model._biosphere[flow_name].target= None
        else:
            raise ValueError(f'Flow {flow_name} not found in technosphere or biosphere.')
    
    def calculate_background_impact(self):
        '''
        Calculate the background impact based on the parameters provided.
        '''
        if self.model._technosphere is None:
            raise ValueError("technosphere dict not created. Define and call 'link_technosphere' first.")
        
        background_flows={}
        for name, ex in self.model._technosphere.items():
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
        self._get_reference()
        self.impact_allocated = {}
        self.impact = {}
        self.impact_dissag =  {}
        for cat in self.method_config['impact_categories']:
            self.impact[cat] = 0
            self.impact_dissag[cat]={}
            #iterate over technosphere flows:
            for name, ex  in self.model._technosphere.items():
                
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

                self.impact_dissag[cat][ex.name]=score
            # iterate over biosphere flows:
            for name, ex in self.model._biosphere.items():
                cf_list=bd.Method(cat).load()
                if ex.source == self.model:
                    factor= [flow for flow in cf_list if flow[0]== ex.target.id]
                
                if ex.target== self.model:
                    factor= [flow for flow in cf_list if flow[0]== ex.source.id]

                if len(factor)!=0:
                    self.impact[cat] += self._get_flow_value(ex)*factor[0][1]

            self.impact_allocated[cat]={}
            # iterate over functional units:
            #if isinstance(self.functional_unit, dict):
            for name, ex in self.model._technosphere.items():
                if not ex.functional:
                    continue
                else:
                    if callable(ex.allocationfactor):
                        allocationfactor= ex.allocationfactor()
                    else:
                        allocationfactor= ex.allocationfactor
                    self.impact_allocated[cat][name] =(
                        self.impact[cat] * 
                        allocationfactor/self._get_flow_value(self.model._technosphere[self._reference_flow])
                        )
                    if ex.impact is None:
                        ex.impact={}
                    ex.impact[cat]=self.impact_allocated[cat][name]

        return self.impact_allocated
    def _get_reference(self):
        '''Sets the reference flow according to technosphere definition. 
        Iterates through the technosphere flows and check for reference flows.
        Raises error if more than one reference flows are defined.
        '''
        ref_list=[name for name, ex  in self.model._technosphere.items()
                  if ex.reference]
        if len(ref_list)>1:
            raise ValueError(f'More than one reference flows. You have to define only one reference flow with `model.set_flow_attr()`. '
                             'The list of flows with reference flows is: {ref_list}.')
        elif len(ref_list)==0:
            raise ValueError(f'No reference flow defined. Use `model.set_flow_attr()` to define exactly one reference flow.')
        else:
            self._reference_flow= ref_list[0]
        
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
            warnings.warn(f"No unit check possible for functional flow {ex.name}. Provide the desired output unit in 'technosphere_edge.model_unit' property.",UserWarning)
            
        # check for unit and transform it in the correct unit if possible.
        # get dataset unit:
        if  ex.target!= None and ex.source!= None:
            if isinstance(ex.dataset_unit, str):
                dataset_unit= ex.dataset_unit
            elif ex.target == self.model and 'unit' in ex.source:
                dataset_unit=ex.source.get('unit')
            elif ex.source == self.model and 'unit' in ex.target:
                dataset_unit=ex.target.get('unit')
            else:
                raise ValueError(f'No dataset unit available for {ex.name}.')
        else:
            
            if not ex.functional:
                dataset_unit= 'NaU'
                raise ValueError(f'No dataset available for {ex.name}.')
            else: 
                if hasattr(ex, 'model_unit') and ex.model_unit!=None and isinstance(ex.model_unit, pint.Unit):
                    dataset_unit= ex.model_unit
                elif hasattr(ex, 'model_unit') and ex.model_unit!=None:
                    dataset_unit= ex.model_unit
                else:
                    dataset_unit='NaU'
                    warnings.warn(f"No unit check possible for functional flow {ex.name}. Provide the desired output unit in 'technosphere_edge.model_unit' property.",UserWarning)
            
        # get model flow unit:
        # if pint quantity:
        if isinstance(amount, pint.Quantity): 
            if  isinstance(dataset_unit, pint.Unit) or dataset_unit in self.model.ureg :
                return amount.m_as(dataset_unit)
            elif dataset_unit not in self.model.ureg:
                #if dataset_unit != ' ':
                warnings.warn(f"The model_unit of {ex.name} got no valid Pint Unit. Ignore unit transformation and internal model unit is choosen.", UserWarning)
                ex.model_unit = amount.u
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
            warnings.warn(f'No unit check possible for {ex.name}. Use pint units if possible or provide pint compatible model unit name.',UserWarning)
            return amount

    def export_to_bw(self, database=None, identifier=None):
        '''Export the model to a brightway dataset.
        Creates the database simulation_model_db if no database is passed. Creates a identifier by the model name, 
        functional unit flow name, and a time stamp if none is passed.

        Args:
            database: Database in which the model activity should be exported. Default is "simodin_db"
            identifier: code for the brightway activity. If empty, the activity code will be created 
                by the name of the mode, the name of the functional flow, and a timestamp.
                If provided but multifunctional, it will create a dataset for each with a code consisting 
                of the name of the functional flow and the provided identifier. 
        '''
        if not hasattr(self, 'impact_allocated'):
            self.calculate_impact()
        
        if database== None:
            database = f"simodin_db" 

        if database not in bd.databases:
            bd.Database(database).register() 
        # iterate over functional flows and create a dataset for each:
        code_list=[]
        for fun_name, fun_ex in self.model._technosphere.items():
            if not fun_ex.functional:
                continue
            now= datetime.datetime.now()
            if identifier==None:
                code= f'{self.name}_{fun_name}_{now}'

            else:
                code= f'{fun_name}_{identifier}'
            code_list.append(code)
            #create a new node in brightway:
            node = bd.Database(database).new_node(
                name= fun_name,
                unit= fun_ex.model_unit,
                code= code,
                **self.model.params
            )
            node.save()
            if callable(fun_ex.allocationfactor):
                allocationfactor= fun_ex.allocationfactor()
            else:
                allocationfactor= fun_ex.allocationfactor
            #iterate over the technosphere flows and create exchanges to the brightway node for each flow:
            for name, ex in self.model._technosphere.items():
                if ex.functional: # only handle not functional flows
                    continue
                #check if technosphere is linked to a bw activity
                if not isinstance(ex.target, bd.backends.proxies.Activity) and ex.source == self.model:
                    continue
                if not isinstance(ex.source, bd.backends.proxies.Activity) and ex.target == self.model:
                    continue
                
                allocated_amount= (self._get_flow_value(ex)*allocationfactor / 
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

            for name, ex in self.model._biosphere.items():
                
                allocated_amount= (self._get_flow_value(ex)*allocationfactor / 
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
        
        return code_list
