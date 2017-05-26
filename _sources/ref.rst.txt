
Reference
=================


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


Plates
-------

.. automodule:: plateo.Plate
   :members:

.. automodule:: plateo.Well
   :members:


Plate parsers
~~~~~~~~~~~~~

From tables
````````````

.. autofunction:: plateo.parsers.plate_from_dataframe
.. autofunction:: plateo.parsers.plate_from_list_spreadsheet
.. autofunction:: plateo.parsers.plate_from_platemap_spreadsheet


From Fragment analyzer data
````````````````````````````
.. autofunction:: plateo.parsers.plate_from_aati_fragment_analyzer_peaktable
.. autofunction:: plateo.parsers.plate_from_aati_fragment_analyzer_zip


Miscellaneous
`````````````
.. autofunction:: plateo.parsers.plate_from_nanodrop_xml_file


Plate Exporters
~~~~~~~~~~~~~~~

.. autofunction:: plateo.exporters.plate_to_bokeh_plot
.. autofunction:: plateo.exporters.plate_to_genesift_sequencing_order_spreadsheet
.. autofunction:: plateo.exporters.plate_to_dataframe
.. autofunction:: plateo.exporters.plate_to_platemap_spreadsheet

Plotters
`````````

.. autofunction:: plateo.exporters.PlateTextPlotter
.. autofunction:: plateo.exporters.PlateColorsPlotter
.. autofunction:: plateo.exporters.PlateGraphsPlotter


.. autofunction:: plateo.parsers.plate_from_roche_lightcycler_qPCR

Container classes
~~~~~~~~~~~~~~~~~~

.. automodule:: plateo.containers.plates
   :members:


Picklists
--------------------------------------------------------------------------

.. automodule:: plateo.PickList
   :members:

Picklist Parsers
~~~~~~~~~~~~~~~~

.. autofunction:: plateo.parsers.picklist_from_labcyte_echo_logfile
.. autofunction:: plateo.parsers.picklist_from_tecan_evo_picklist_file
   :members:


Tools
-------------------------------------------------

.. automodule:: plateo.tools
   :members:
