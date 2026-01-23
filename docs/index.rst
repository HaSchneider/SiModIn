

=======
SiModIn
=======


This is the documentation of **SiModIn**: 

   **Si**\ mulation **Mod**\ el **In**\ terface 

An interface between simulation models and 
`brightway25 <https://docs.brightway.dev/en/latest/>`_.


..  figure:: /_static/images/simodin.svg
    :alt: simodin logo
    :align: right
    :class: only-light

..  figure:: /_static/images/simodin_3_dark.svg
    :alt: simodin logo
    :align: right
    :class: only-dark

**SiModIn** can be used to:

* Create generic model based brightway25 datasets.
* Calculate the impact of your models.
* Provide your simulation models for LCA studies.

Using simulations for Life cycle Assessment (LCA) studies can help to improve 
the quality of LCA datasets by providing parameterized and detailed data of specific process systems.
Unlike generic datasets, which represent a market average, simulation based datasets can be tailored
to reflect specific technologies, geographical locations, or operational conditions. This allows a detailed
and accurate representation of the environmental impacts associated with a product or service throughout 
its life cycle.
SiModIn aims to facilitate the integration of simulation models into LCA workflows, 
enabling more accurate and comprehensive environmental impact assessments.

By a flexible interface, SiModIn allows users to connect various simulation tools
with brightway25, making it easier to incorporate simulation results into LCA analyses.

Its generic design allows to use SiModIn with different simulation software,
such as `TESPy <https://tespy.readthedocs.io/en/main/>`_, `DWSIM <https://dwsim.org/>`_ 
or other tools that can be controlled via Python. On the other hand it allows SiModIn 
models to be shared and reused by other LCA practitioners, without the need to be a 
professional user of the underlying simulation software.






Contents
========

.. toctree::
   :maxdepth: 1
   :caption: Getting started

   Gettingstarted <getting_started>

.. toctree::
   :maxdepth: 2
   :caption: Learn SiModIn
   
   Tutorials <tutorial>
   

.. toctree::
   :maxdepth: 2
   :caption: About SiModIn

   License <license>
   Authors <authors>
   Changelog <changelog>
   Module Reference <api/modules>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _toctree: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html
.. _reStructuredText: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
.. _references: https://www.sphinx-doc.org/en/stable/markup/inline.html
.. _Python domain syntax: https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#the-python-domain
.. _Sphinx: https://www.sphinx-doc.org/
.. _Python: https://docs.python.org/
.. _Numpy: https://numpy.org/doc/stable
.. _SciPy: https://docs.scipy.org/doc/scipy/reference/
.. _matplotlib: https://matplotlib.org/contents.html#
.. _Pandas: https://pandas.pydata.org/pandas-docs/stable
.. _Scikit-Learn: https://scikit-learn.org/stable
.. _autodoc: https://www.sphinx-doc.org/en/master/ext/autodoc.html
.. _Google style: https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
.. _NumPy style: https://numpydoc.readthedocs.io/en/latest/format.html
.. _classical style: https://www.sphinx-doc.org/en/master/domains.html#info-field-lists
