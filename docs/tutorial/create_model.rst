
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

In this example, replace :code:`your_simodin_model_class` with the desired name for your model class. Implement the :code:`init_model`, :code:`calculate_model`, and :code:`define_flows` methods with the specific logic for your simulation model.

**init_model:**

This method should contain the code to initialize your simulation model, such as setting up parameters or loading data. 

**calculate_model:** 

This method should contain the code to run your simulation model, performing the necessary calculations or simulations.

**define_flows:**

This method should define the flows of your model which needs to be considered in the LCA calculation. Those flows can be linked to brightway25 datasets in the concrete modelInterface class.
SiModIn extractors can be used for specific software to extract typical flows automatically. This is be done for example for tespy models by using the class :code:`simodin.extractors.tespy.extract_technosphere_flows`.

For conducting LCA calculations, minimum one functional unit must be defined and exact one reference flow by the set_flow_attr method:

.. code-block:: python

    from simodin import  tespy
    
    class your_simodin_model_class(SimModel):
    
        def define_flows(self):
            # Extract flows automatically:
            self.technosphere = tespy.extract_technosphere_flows(self)
            
            # or create them manually:
            self.technosphere['fuel source'].amount = lambda: (self.model.get_conn('5').v._val
                                        * self.model.units.ureg.hour
                                        ).to('meter**3')

            # Define functional and reference flow:
            self.set_flow_attr('flow_name', 'functional', True)
            self.set_flow_attr('flow_name', 'reference', True)

After defining your model class, you can instantiate and use it in your application as shown in the "Use SiModIn models" tutorial.

