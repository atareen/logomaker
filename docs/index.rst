=============================================================================
Logomaker: Software for the visualization of sequence-function relationships
=============================================================================

*Written by Ammar Tareen, and Justin B. Kinney.*

Logomaker is a Python application programming interface (API) for generating publication-quality sequence logos.
Sequence logos are a popular way of representing a variety of sequence-function relationships.
Currently available Python applications for making sequence logos are optimized only for specific
experiments, and thus are limited in their usage.Logomaker can generate
logos from a variety of data including multiple sequence alignments, enrichment data from massively
parallel reporter assays (MPRAs) and deep mutational scanning (DMS) experiments. Logomaker logos
are generated as native matplotlib axes objects that are amenable to subsequent customization and
incorporation into multi-panel figures.

.. toctree::
   :maxdepth: 2
   :caption: Contents:


Installation
------------

logomaker can be installed from
`PyPI <https://pypi.python.org/pypi/logomaker>`_ using the pip package
manager. At the command line::

    pip install logomaker

The code for logomaker is open source and available on
`GitHub <https://github.com/jbkinney/logomaker>`_.


Documentation
-------------


.. toctree::
   :maxdepth: 2

   Logo
   Glyph
   matrix

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
