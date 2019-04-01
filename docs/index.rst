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

Examples
--------

.. image:: _static/Saliency.png
   :scale: 30 %

.. image:: _static/RNAP.png
   :scale: 30 %

.. image:: _static/Najafi.png
   :scale: 30 %


Installation
------------

logomaker can be installed from
`PyPI <https://pypi.python.org/pypi/logomaker>`_ using the pip package
manager. At the command line::

    pip install logomaker

The code for logomaker is open source and available on
`GitHub <https://github.com/jbkinney/logomaker>`_.


Classes and Functions Documentation
===================================

.. toctree::
   :maxdepth: 2

   Logo
   Glyph
   matrix

Contact
-------

For technical assistance or to report bugs, please
contact `Ammar Tareen <tareen@cshl.edu>`_.

For more general correspondence, please
contact `Justin Kinney <jkinney@cshl.edu>`_.

Other links:

- `Kinney Lab <http://kinneylab.labsites.cshl.edu/>`_
- `Simons Center for Quantitative Biology <https://www.cshl.edu/research/quantitative-biology/>`_
- `Cold Spring Harbor Laboratory <https://www.cshl.edu/>`_


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
