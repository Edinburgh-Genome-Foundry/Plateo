
.. raw:: html

    <p align="center">
    <img alt="Plateo Logo" title="Plateo Logo" src="https://raw.githubusercontent.com/Edinburgh-Genome-Foundry/Plateo/master/docs/_static/images/title.png" width="400">
    <br /><br />
    </p>

.. image:: https://github.com/Edinburgh-Genome-Foundry/Plateo/actions/workflows/build.yml/badge.svg
    :target: https://github.com/Edinburgh-Genome-Foundry/Plateo/actions/workflows/build.yml
    :alt: GitHub CI build status

.. image:: https://coveralls.io/repos/github/Edinburgh-Genome-Foundry/Plateo/badge.svg?branch=master
  :target: https://coveralls.io/github/Edinburgh-Genome-Foundry/Plateo?branch=master


Plateo (pronounced *Plato*, like the planet) is a Python library to assist in the
planning, running and checking of laboratory experiments involving microplates.

It can be used to:

- Read and write robotic protocols (picklists) in different formats to
  accomodate different liquid dispensers (Tecan EVO, Labcyte Echo).
- Simulate liquid dispensing runs, taking into account the capacity and dead
  volume of each container, to predict the maps of future plates.
- Parse plate data from common laboratory robots (for kinetic experiments,
  fragment analysis, qPCR, etc.)
- Export plate information in various formats (graphics, spreadsheets, HTML,
  JSON, etc.).


Work in progress - contribute !
-------------------------------

Plateo is an open-source software originally written at the `Edinburgh Genome Foundry
<http://www.genomefoundry.io>`_ (an academic platform) by `Zulko <https://github.com/Zulko>`_
and `released on Github <https://github.com/Edinburgh-Genome-Foundry/plateo>`_
under the MIT licence (Copyright 2017 Edinburgh Genome Foundry).

It was released in the hope that it will be as useful for other automated labs as it is for use,
but keep in mind that it is still under development, the features and docs will get better.

Plateo aims at collecting parsers and export routines to speak to any kind of
automated equipment. If you have written parsers that don't appear in Plateo,
we are happy to hear about it. If you need help writing parsers for your favorite
robot, we may be able to help too!


Installation
------------

Plateo can be installed from the Python Package Index with PIP: ::

    pip install plateo

It can also be installed by unzipping the source code in one directory and using this command: ::

    python setup.py install


Code organization
-----------------

- ``Plate.py``, ``Well.py`` and ``Picklist.py`` implement the central objects
  ``Plate``, ``Well``, and ``Picklist``.
- The ``containers`` folder contains specific classes of ``Plate`` and ``Well``
  will predefined dimensions, capacity, dead volume, etc.
- The ``parsers`` folder contains all methods to generate Plates or Picklists
  from machine files and data.
- The ``exporters`` folder contains all methods to export plates in picklists
  in human- or machine-readable format.
