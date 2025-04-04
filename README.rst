
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


Plateo is a Python library that assists in the planning of laboratory experiments involving microplates.

It can be used to:

- Model laboratory microplates, well contents and liquid transfers.
- Read and write robotic protocols (picklists) in different formats to
  accomodate different liquid dispensers (Tecan EVO, Labcyte Echo).
- Simulate liquid dispensing runs, taking into account the capacity and dead
  volume of each container, to predict the maps of future plates.
- Parse plate data from common laboratory robots (for kinetic experiments,
  fragment analysis, qPCR, etc.)
- Export plate information in various formats (graphics, spreadsheets, HTML,
  JSON, etc.).
- Create detailed report on various complex operations.


Install
-------

Plateo can be installed from the Python Package Index: ::

    pip install plateo


Code organization
-----------------

- Plateo is organised around various lab containers and liquid transfers between them.
- The ``containers`` folder has the ``Well`` and ``WellContent`` classes, which
  model microplate wells and their contents. The ``Plate`` class models laboratory
  microplates. Built-in plates with predefined dimensions, capacity, dead volume, etc.
  are also stored in this folder.
- The ``transfers`` folder contents simulate liquid transfers (``Transfer``) and lists 
  of transfers (``PickList``).
- The ``parsers`` folder contains all methods for generating Plates or Picklists
  from machine files and data.
- The ``exporters`` folder contains all methods for exporting Plates or PickLists
  into human- or machine-readable formats.
- The ``applications`` folder contains complex procedures with input/output operations;
  such as creating a DNA assembly picklist and related documentation.


Versioning
----------

Plateo uses the `semantic versioning <https://semver.org>`_ scheme.


License = MIT
-------------

Plateo is `free software <https://www.gnu.org/philosophy/free-sw.en.html>`_, which means
the users have the freedom to run, copy, distribute, study, change and improve the software.

Plateo was originally written by `Zulko <https://github.com/Zulko>`_ at the `Edinburgh Genome Foundry <http://www.genomefoundry.io>`_ and is currently being developed by `Peter Vegh <https://github.com/veghp>`_.
It is released under the MIT license (Copyright 2017 Edinburgh Genome Foundry, University of Edinburgh).
