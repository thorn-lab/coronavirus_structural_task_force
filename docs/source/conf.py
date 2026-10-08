# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
import os

sys.path.insert(0, os.path.abspath("../../src"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "cstf"
copyright = "2026, ThornLab"
author = "ThornLab"
release = "0.0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_autodoc_typehints",
]

autodoc_typehints = "description"
autodoc_typehints_format = "short"
python_use_unqualified_type_names = True
add_module_names = False
autodoc_member_order = "bysource"
myst_enable_extensions = ["colon_fence"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/version/2.3", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "aiohttp": ("https://docs.aiohttp.org/en/stable/", None),
    "seaborn": ("https://seaborn.pydata.org/", None),
    "rcsbapi": ("https://rcsbapi.readthedocs.io/en/latest/", None),
}


templates_path = ["_templates"]
exclude_patterns = []

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
