.. © 2023 Fraunhofer-Gesellschaft e.V., München
..
.. SPDX-License-Identifier: AGPL-3.0-or-later

.. This is the main entry point for the source files of our user documentation.
  This file is written in reStructuredText *.rst and used by Sphinx.
  The included *.md files are written in MyST, a markdown flavor. We prefer
  using markdown content. This main/index file needs to be in rst.
  The generated documentation is located at
  * doc/build/html/index.html
  * doc/build/pdf/index.pdf

Welcome to MICAT's documentation!
=======================================

The documentation explains the methodology and workflow of the MICATool. Furthermore, it explains the coding in order to
facilitate improvements by other users and explains the assumptions and methodologies of the implemented indicators.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   introduction/introduction
   user_interface/user_interface_description
   indices/indices_description
   energy_mix/energy_mix_description
   social_indicators/social_indicators_description
   economic_indicators/economic_indicators_description
   ecologic_indicators/ecologic_indicators_description
   api/api

.. only:: html

  * :doc:`./list_of_pages`


