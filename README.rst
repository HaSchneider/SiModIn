.. These are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://readthedocs.org/projects/simodin/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://simodin.readthedocs.io/en/stable/
    .. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
        :alt: Project generated with PyScaffold
        :target: https://pyscaffold.org/


.. image:: https://img.shields.io/pypi/v/simodin.svg
    :alt: PyPI-Server
    :target: https://pypi.org/project/simodin/

.. image:: https://img.shields.io/badge/brightway-25-83d299
    :alt: brightway: 25
    :target: https://github.com/brightway-lca/brightway25


.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :alt: License: MIT
    :target: https://opensource.org/licenses/MIT
 

..  figure:: /images/simodin.svg
    :alt: simodin logo


=======
SiModIn
=======

   **Si**\ mulation **Mod**\ el **In**\ terface 
    Interface between simulation models and `brightway25 <https://docs.brightway.dev/en/latest/>`_.




**SiModIn** can be used to:

* Create simulation based brightway25 datasets.
* Calculate the impact of your models.
* Provide your simulation models for LCA studies.

=================
Installation
=================

Install SiModIn from PyPi:

.. code-block:: python

   pip install simodin

=================
Getting started
=================

The basic usage of SiModIn will be presented for an Tespy powerplant model from the offical `Tespy documentation <https://tespy.readthedocs.io/en/main/tutorials/pygmo_optimization.html>`_.


To use the existing SiModIn model, import and instantiate the SimModel class: 

.. code-block:: python

   from SimModel_powerplant import tespy_model
   from simodin import interface as link

   my_model= tespy_model('powerplant')
   

Then inititate the model and calculate it. 

.. code-block:: python

   my_model.init_model()
   my_model.calculate_model()

Create the technosphere dictionary and pass the model to an modelInterface instance.    

.. code-block:: python

   my_model.define_flows()

   my_interface= link.modelInterface('tespy powerplant',my_model)

For LCA calculation, the needed brightway25 dataset needs to be assigned to the technosphere flows:

.. code-block:: python

   import bw2data as bd
   
   bd.projects.set_current('bw_meets_tespy')
   my_interface.methods=[('ecoinvent-3.11',  'EF v3.1',  'climate change',  'global warming potential (GWP100)')]
   ei=bd.Database('ecoinvent-3.11-cutoff')

   ei_heat=[act for act in ei if 'heat production, at hard coal industrial furnace 1-10MW' in act['name']
    and 'Europe without Switzerland' in act['location'] ][0]

   ei_water=[act for act in ei if 'market for tap water' in act['name']
    and 'Europe without Switzerland' in act['location'] ][0]

   my_interface.add_dataset('heat source', ei_steam)
   my_interface.add_dataset('cooling water source', ei_water)
   my_model.set_flow_attr('cooling water source', 'dataset_correction', 0.1)

After that, the LCA calculation can be executed or the data exported to a brightway25 database:

.. code-block:: python

   my_interface.calculate_background_impact()
   my_interface.calculate_impact()
   code= my_interface.export_to_bw()

This and further examples how to use SiModIn can be found `here <https://github.com/HaSchneider/awesome-simodin-models/tree/main/Examples>`_.
