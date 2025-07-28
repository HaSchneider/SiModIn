.. These are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://readthedocs.org/projects/simodin/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://simodin.readthedocs.io/en/stable/
    .. image:: https://img.shields.io/pypi/v/simodin.svg
        :alt: PyPI-Server
        :target: https://pypi.org/project/simodin/

   .. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
       :alt: Project generated with PyScaffold
       :target: https://pyscaffold.org/

|

=======
SiModIn
=======


    Simulation Model Interface 


Interface between simulation models and `brightway25 <https://docs.brightway.dev/en/latest/>`_.

=================
Getting started
=================

To use an existing SiModIn model, import the model and instantiate it. 

This will be shown for an Tespy model from the `Tespy documentation <https://tespy.readthedocs.io/en/main/tutorials/pygmo_optimization.html>`_:

.. code-block:: python

   from simodin import interface as link
   from tespy_example import tespy_model

   my_model= tespy_model('powerplant')
   my_model.init_model()

Than inititate the model and calculate it. Afterwards, create the technosphere dictionary and assign the model to an modelInterface instance.    

.. code-block:: python

   my_model.calculate_model()
   my_model.technosphere

   my_interface= link.modelInterface('tespy powerplant',my_model)

For LCA calculation, the needed brightway25 dataset needs to be linked to the technosphere flows:

.. code-block:: python

   import bw2data as bd
   
   bd.projects.set_current('bw_meets_tespy')
   my_interface.methods=[('ecoinvent-3.11',  'EF v3.1',  'climate change',  'global warming potential (GWP100)')]
   ei=bd.Database('ecoinvent-3.11-cutoff')

   ei_heat=[act for act in ei if 'heat production, at hard coal industrial furnace 1-10MW' in act['name']
    and 'Europe without Switzerland' in act['location'] ][0]
   my_interface.technosphere['heat source'].source=ei_heat

   ei_water=[act for act in ei if 'market for tap water' in act['name']
    and 'Europe without Switzerland' in act['location'] ][0]

   my_interface.technosphere['cooling water source'].source=ei_water
   my_interface.technosphere['cooling water source'].dataset_correction = 0.1 #blowdown rate

After that, the LCA calculation can be executed or the data exported to a brightway25 database:

.. code-block:: python

   my_interface.calculate_background_impact()
   my_interface.calculate_impact()
   code= my_interface.export_to_bw()

This and further examples how to use SiModIn can be found `here <https://github.com/HaSchneider/SiModIn/tree/main/src/simodin/Examples>`_.
