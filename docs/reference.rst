#############
API Reference
#############

WdBibTeX
========

.. currentmodule:: wdbibtex

Constructor
-----------

.. autosummary::
   :toctree: _api

   WdBibTeX

Methods
-------
.. autosummary::
   :toctree: _api

   WdBibTeX.close
   WdBibTeX.compile
   WdBibTeX.find_all
   WdBibTeX.open_doc
   WdBibTeX.replace_all


LaTeXHandler
============

.. currentmodule:: wdbibtex

Constructor
-----------

.. autosummary::
   :toctree: _api

   LaTeXHandler

Attributes
----------
.. autosummary::
   :toctree: _api
   
   LaTeXHandler.thebibliography_text

Methods
-------
.. autosummary::
   :toctree: _api

   LaTeXHandler.build_conversion_dict
   LaTeXHandler.compile
   LaTeXHandler.get_dashed_range
   LaTeXHandler.get_locale
   LaTeXHandler.get_replacer
   LaTeXHandler.parse_aux
   LaTeXHandler.parse_line
   LaTeXHandler.read_bbl
   LaTeXHandler.write
