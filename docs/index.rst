EJBCA-REST
==========

|License badge| |Docker badge|

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :glob:

   profile-configuration
   api
   building-documentation

Index
-----

-  `Description <#description>`__
-  `Dependences <#dependences>`__
-  `Configuration <#configuration>`__

 
Description
------------

This is a utility library to simplify the call for EJBCA SOAP API with
a more modern and easy to use REST JSON API.

Dependencies
------------

pip install zeep

(optional) for the docs: pip install aglio


Configuration
--------------

Configuring EJBCA Profiles
~~~~~~~~~~~~~~~~~~~~~~~~~~

EJBCA-REST is configurated out of the box with Certification Profiles
compatible with Mosquitto TLS and other IoT Brokers.

If you need to configure EJBCA manualy, check our :doc:`profile-configuration`.

.. |License badge| image:: https://img.shields.io/badge/license-GPL-blue.svg
   :target: https://opensource.org/licenses/GPL-3.0
.. |Docker badge| image:: https://img.shields.io/docker/pulls/dojot/ejbca.svg
   :target: https://hub.docker.com/r/dojot/ejbca/
