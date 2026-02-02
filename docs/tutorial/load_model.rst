.. load_model:

##################
Use SiModIn models  
##################

In this tutorial the setup of SiModIn models is shown. Furthermore the calculation of the LCA scores of the models, 
and the export to brightway25 datasets is described with an example.  

Initialization
"""""""""""""""

To use an existing SiModIn model, import and initialize the :code:`SimModel` class:

.. code-block:: python

   from simodin import interface as link
   from your_simodin_model_file import your_simodin_model_class

   my_model= your_simodin_model_class('model_name')

With the attributes:

- :code:`name`: Name of the model.
- :code:`init_arg`: Initialization arguments for the model.
- :code:`**model_params`: Model Parameter.

Then initialize and calculate the model by calling the respective methods:

.. code-block:: python

   my_model.init_model()
   my_model.calculate_model()


LCA setup
""""""""""

With :code:`define_flows`, the flows of the model can be set up for LCA calculations:

.. code-block:: python

   my_model.define_flows()

For the LCA calculations, create a :code:`modelInterface` instance by passing the model name and the SiModIn model object:

.. code-block:: python

   my_interface= link.modelInterface('model_name',my_model)

The :code:`modelInterface` class links the SiModIn model to Brightway2 for LCA calculations. After initializing and calculating the model, call the :code:`define_flows` method to set up the flows for LCA. 
The LCA datasets can then be added to the model interface using the :code:`add_dataset` method:

.. code-block:: python

    my_interface.add_dataset('technosphere_flow_A', bw25_activity_A)
    my_interface.add_dataset('technosphere_flow_B', bw25_activity_B)

For the LCIA, the impact categorization method needs to be set by set the :code:`methods` property.

.. code-block:: python

    #define impact method:
    my_interface.methods=[('ecoinvent-3.11',  
            'EF v3.1',  
            'climate change',  
            'global warming potential (GWP100)')]


LCA calculation
""""""""""""""""

The impact can be calculated by calling :code:`calculate_background_impact` method, followed by the :code:`calculate_impact` method:

.. code-block:: python

   my_interface.calculate_background_impact()
   total_impact = my_interface.calculate_impact()
   print("Total Impact:", total_impact)

.. admonition:: Unit transformation
   :class: tip

   An unit transformation logic based on `Pint <https://pint.readthedocs.io/en/stable/>`_ is implemented in the :code:`modelInterface` classs. 
   This works only when all of the following requirements are met:
   
   - brightway dataset:
     
     1. the flow got a :code:`unit` property which is compatible with the `default Pint units <https://github.com/hgrecco/pint/blob/master/pint/default_en.txt>`_
     2. or the linked brightway activity got a :code:`unit` property which is compatible with the `default Pint units <https://github.com/hgrecco/pint/blob/master/pint/default_en.txt>`_
   
   - model flow:

     1. the value returned by the model flow property :code:`amount` is a Pint quantity
     2. or the model flow property :code:`model_unit` is defined and is compatible with the `default Pint units <https://github.com/hgrecco/pint/blob/master/pint/default_en.txt>`_

   The units must be compatible, otherwise an error is raised. 

   If the requirements are not met, a warning is raised and no transformation is done. 

Export to a brightway25 dataset
""""""""""""""""""""""""""""""""

Then, the model result can be exported to a brightway25 activity using the :code:`export_to_bw` method. 
The name of the activity can be passed as an argument, or it will use a string created by the model name, 
the name of the functional unit and a time stamp. 
The brightway25 database can also be specified, otherwise the default database :code:`simodin_db` will be used.

.. code-block:: python

    code= my_interface.export_to_bw(
            activity_name='my_simodin_model_activity', 
            database_name='my_simodin_db')
