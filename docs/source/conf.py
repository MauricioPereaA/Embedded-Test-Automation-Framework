# -*- coding: utf-8 -*-
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os

# set sphinxdoc flag to True
os.environ["SPHINX_DOC_MODE"] = "1"

project = "TAF's Test Automation Framework"
copyright = "2023, Mauricio Perea"
author = "Mauricio Perea"
release = "2023.02.16"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinxcontrib.jquery",
    "sphinx_rtd_theme",
    "sphinx.ext.autodoc",
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

import sys
import pathlib

# base_path = pathlib.Path(__file__).parent.parent.parent
# print(f"adding base path as {base_path}")
# sys.path.insert(0, base_path)

import DTAF
