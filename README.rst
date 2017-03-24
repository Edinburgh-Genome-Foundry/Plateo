Plateo
======

Plateo (pronounced Plato, like the Planet) is a Python library to assist in the
planning, running and checking of laboratory experiments involving microplates.

It can be used to:

- Read and write robotic protocols (picklists) in different formats to accomodate different liquid dispensers (Tecan EVO, Labcyte Echo).
- Simulate liquid dispensing runs, taking into account the capacity and dead volume of each container, to predict the maps of future plates.
- Parse plate data from common laboratory robots (for kinetic experiments, fragment analysis, qPCR, etc.)
- Export plate information in various formats (graphics, spreadsheets, HTML, JSON, etc.).

Installation
--------------

Plateo can be installed by unzipping the source code in one directory and using this command: ::

    (sudo) python setup.py install

You can also install it directly from the Python Package Index with this command: ::

    (sudo) pip install plateo

Code organization
------------------

- ``Plate.py``, ``Well.py`` and ``Picklist.py`` implement the central objects
  ``Plate``, ``Well``, and ``Picklist``.
- The ``containers`` folder contains specific classes of ``Plate`` and ``Well``
  will predefined dimensions, capacity, dead volume, etc.
- The ``parsers`` folder contains all methods to generate Plates or Picklists
  from machine files and data.
- The ``exporters`` folder contains all methods to export plates in picklists
  in human- or machine-readable format.


Contribute
-----------

Plate Converter is originally written by Zulko for the Edinburgh Genome Foundry and released under the MIT licence.
Everyone is welcome to contribute
