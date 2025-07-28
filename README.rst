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


To use a SiModIn model:

.. code-block:: python

   from simodin import interface as link
   import my_model
   model = my_model(name= 'my SiModIn model')
   model.init_model()
   model.calculate_model()
   model.technosphere

   my_interface = link.modelInterface(model= model, name= 'my SiModIn interface')


Further examples how to use SiModIn can be found `here <https://github.com/HaSchneider/SiModIn/tree/main/src/simodin/Examples>`_
