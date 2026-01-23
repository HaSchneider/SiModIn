
.. create_model:

#####################
Create SiModIn models
#####################

To create your own SiModIn model, create a new python file and import the :code:`SimModel` base class:

.. code-block:: python

   from simodin import SimModel

   class your_simodin_model_class(SimModel):
       def __init__(self, name):
           super().__init__(name)
           # Your model specific initializations here

       def init_model(self):
           # Code to initialize your simulation model

       def calculate_model(self):
           # Code to run your simulation model

       def define_flows(self):
           # Code to define the flows for your model

In this example, replace :code:`your_simodin_model_class` with the desired name 
for your model class. Implement the :code:`init_model`, :code:`calculate_model`, 
and :code:`define_flows` methods with the specific logic for your simulation model.
The setup of a model will be demonstrated on the Gas turbine example from 
`Tespy documentation <https://tespy.readthedocs.io/en/main/basic_tutorials/gas_turbine.html>`_. 
The full code is available `here <https://github.com/HaSchneider/awesome-simodin-models/tree/main/Examples/tespy/gas_turbine>`_.

Import dependencies:
""""""""""""""""""""

.. code-block:: python

    from simodin import interface as link
    from simodin import tespy 

    from tespy.networks import Network
    from tespy.components import (
        DiabaticCombustionChamber, Turbine, Source, Sink, Compressor,
        Generator, PowerBus, PowerSink
    )
    from tespy.connections import Connection, Ref, PowerConnection

Provide model reference as class attribute.
"""""""""""""""""""""""""""""""""""""""""""

Reference can be passed to the model by using the class attribute :code:`reference`. 
A bibtex like dictionary with reference informations can be passed here.
Aditionally, needed parameter can be defined here with defaul values in the :code:`parameter` dictionary attribute. 

.. code-block:: python

    class tespy_model(link.SimModel):
        reference= { 
            'type': 'misc',
            'key': 'tespy_gas_turbine',
            'author' :'Francesco Witte',
            'title'  : 'Gas Turbine',
            'url': 'https://tespy.readthedocs.io/en/main/basic_tutorials/gas_turbine.html'
            }

        parameter={
            'heat_output':100*self.model.units.ureg.MJ,
            'lifetime_turbine':80000*self.model.units.ureg.hour, #lifetime in hours
            }

Implementation of the concrete methods:
""""""""""""""""""""""""""""""""""""""""

**init_model:**

This method contain the code to initialize your simulation model, 
such as setting up parameters or loading data. In this example the Tespy
network is build here. The key word argument :code:`heat_output` is used 
as model parameter to define the heat output at the combustion chamber.


.. code-block:: python

       def init_model(self,  **params):
            self.model = Network()
            self.model.units.set_defaults(temperature='degC', pressure='bar', enthalpy='kJ / kg')
            self.model.units.ureg.define('m3 = meter**3')
            cp = Compressor("Compressor")
            cc = DiabaticCombustionChamber("combustion chamber")
            tu = Turbine("turbine")
            air = Source("air source")
            fuel = Source("fuel source")
            fg = Sink("flue gas sink")
            c1 = Connection(air, "out1", cp, "in1", label="1")
            c2 = Connection(cp, "out1", cc, "in1", label="2")
            c3 = Connection(cc, "out1", tu, "in1", label="3")
            c4 = Connection(tu, "out1", fg, "in1", label="4")
            c5 = Connection(fuel, "out1", cc, "in2", label="5")
        
            cc.set_attr(pr=1, eta=1, lamb=1.5, ti=self.params['heat_output'])
            c5.set_attr(p=1, T=25, fluid={"CO2": 0.04, "CH4": 0.96, "H2": 0})
            
            self.model.add_conns(c1, c2, c3, c4, c5)

            generator = Generator("generator")
            grid = PowerSink("grid")
            shaft = PowerBus("shaft", num_in=1, num_out=2)

            e1 = PowerConnection(tu, "power", shaft, "power_in1", label="e1")
            e2 = PowerConnection(shaft, "power_out1", cp, "power", label="e2")
            e3 = PowerConnection(shaft, "power_out2", generator, "power_in", label="e3")
            e4 = PowerConnection(generator, "power_out", grid, "power", label="e4")

            self.model.add_conns(e1, e2, e3, e4)

            generator.set_attr(eta=0.98)
            cp.set_attr(eta_s=0.85, pr=15)
            tu.set_attr(eta_s=0.90)
            c1.set_attr(
                p=1, T=25,
                fluid={"Ar": 0.0129, "N2": 0.7553, "CO2": 0.0004, "O2": 0.2314}
            )
            #c3.set_attr(m=30)
            c4.set_attr(p=Ref(c1, 1, 0))



**calculate_model:** 

This method contain the code to run your simulation model, performing the 
necessary calculations or simulations.

In this example it contains the solve() method of the tespy network. 

.. code-block:: python 

    def calculate_model(self):
        self.model.solve("design")
        
        # unset the value, set Referenced value instead
        self.model.get_conn('5').set_attr(p=None)
        self.model.get_conn('5').set_attr(p=Ref(self.model.get_conn('2'), 1.05, 0))
        self.model.solve("design")


**define_flows:**

This method should define the flows of your model which needs to be considered in 
the LCA calculation. Those flows can be linked to brightway25 datasets in the 
concrete modelInterface class. SiModIn extractors can be used for specific 
software to extract typical flows automatically. This is be done for example for tespy 
models by using the class :code:`simodin.extractors.tespy.extract_technosphere_flows`.

For conducting LCA calculations, minimum one functional unit must be defined and 
exact one reference flow by the set_flow_attr method:

.. code-block:: python

    def define_flows(self):
        
        #get all technosphere flows:
        technosphere=tespy.extract_technosphere_flows(self)
        '''
        Add a flow for the fuel source and convert it to a volume, 
        as most generic datasets are not using flows as reference value:
        '''
        technosphere['fuel source'].amount = lambda: (self.model.get_conn('5').v._val
                                        * self.model.units.ureg.hour
                                        ).to('meter**3')
        
        # remove not needed flows: 
        del technosphere['flue gas sink']
        
        #set functional unit and reference flow:
        technosphere['grid'].functional = True
        technosphere['grid'].reference = True
        self.technosphere = technosphere
        
        # add biosphere flows:
        biosphere={}
        biosphere['flue gas sink']=link.biosphere_edge(
            name='flue gas sink',
            source= self,
            target= None,
            amount=lambda: (self.model.get_conn('4').m._val*self.model.get_conn('4').fluid.val['CO2']
                                        * self.model.units.ureg.hour
                                        ).to('kg'),
        )
        self.biosphere= biosphere
        '''
        Add a technosphere flow representing the impact of the equipment. 
        This can be done by the setter method:
        '''
        self.add_flow(link.technosphere_edge(
            name = 'turbine equipment',
            source = None,
            target = self,
            amount= lambda: (self.model.get_conn('e3').E._val * 
                    self.model.units.ureg.hour /self.params['lifetime_turbine']
                    ),
            description= (
                'Impact of the turbine equipment. Link a dataset with the' +
                'production of a turbine with a suitable power as functional unit')
        ))


Load the model
""""""""""""""

After defining your model class, you can instantiate and use it in your 
application as shown in the :doc:`"Use SiModIn models" <load_model>` 
tutorial.

