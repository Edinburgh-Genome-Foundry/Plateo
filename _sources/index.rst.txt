Plateo Documentation
==========================

.. image:: _static/images/title.png
   :width: 400px
   :align: center

Plateo (pronounced *Plato*, like the planet) is a Python library to assist in the
planning, running and checking of laboratory experiments involving microplates.

It can be used to:

- Read and write robotic protocols (picklists) in different formats to accomodate
  different liquid dispensers (Tecan EVO, Labcyte Echo).
- Simulate liquid dispensing runs, taking into account the capacity and dead
  volume of each container, to predict the maps of future plates.
- Parse plate data from common laboratory robots (for kinetic experiments,
  fragment analysis, qPCR, etc.)
- Export plate information in various formats (graphics, spreadsheets, HTML,
  JSON, etc.).

The following schema shows how Plateo's file parsers, exporters, and protocol
simulator work together

.. image:: _static/images/general_schema.png
   :width: 800px
   :align: center


Work in progress - contribute !
-------------------------------

Plateo is an open-source software originally written at the `Edinburgh Genome Foundry
<http://www.genomefoundry.io>`_ (an academic platform) by `Zulko <https://github.com/Zulko>`_
and `released on Github <https://github.com/Edinburgh-Genome-Foundry/plateo>`_
under the MIT licence (¢ Edinburgh Genome Foundry).

It was released in the hope that it will be as useful for other automated labs as it is for use,
but keep in mind that it is still under development, the features and docs will get better.

Plateo aims at collecting parsers and export routines to speak to any kind of
automated equipment. If you have written parsers that don't appear in Plateo,
we are happy to hear about it. If you need help writing parsers for your favorite
robot, we may be able to help too !


Installation
--------------

Plateo can be installed by unzipping the source code in one directory and using this command: ::

   (sudo) python setup.py install

You can also install it directly from the Python Package Index with this command: ::

   (sudo) pip install plateo


.. raw:: html

       <a href="https://twitter.com/share" class="twitter-share-button"
       data-text="Plateo - Parsers, Reports, simulations and file generators for lab automation" data-size="large" data-hashtags="Bioprinting">Tweet
       </a>
       <script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';
       if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src=p+'://platform.twitter.com/widgets.js';
       fjs.parentNode.insertBefore(js,fjs);}}(document, 'script', 'twitter-wjs');
       </script>
       <iframe src="http://ghbtns.com/github-btn.html?user=Edinburgh-Genome-Foundry&repo=plateo&type=watch&count=true&size=large"
       allowtransparency="true" frameborder="0" scrolling="0" width="152px" height="30px" margin-bottom="30px"></iframe>


.. toctree::
    :hidden:
    :maxdepth: 3

    self

.. toctree::
    :hidden:
    :caption: Reference
    :maxdepth: 3

    ref


.. _Zulko: https://github.com/Zulko/
.. _Github: https://github.com/EdinburghGenomeFoundry/bandwitch
.. _PYPI: https://pypi.python.org/pypi/bandwitch
