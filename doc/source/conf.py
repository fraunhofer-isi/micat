# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'MICAT'
# noinspection PyShadowingBuiltins
copyright = '2023, Fraunhofer'
author = 'Frederic Berger, Stefan Eidelloth'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',  # Also see https://myst-parser.readthedocs.io/en/latest/intro.html
    'rst2pdf.pdfbuilder',  # Also see https://github.com/rst2pdf/rst2pdf
    'sphinx.ext.autosectionlabel', # Also see https://www.sphinx-doc.org/en/master/usage/extensions/autosectionlabel.html
]

# myst parser syntax extensions, also see https://myst-parser.readthedocs.io/en/latest/syntax/optional.html
myst_enable_extensions = [
    "amsmath",
    #"attrs_inline",
    #"colon_fence",
    #"deflist",
    "dollarmath",
    #"fieldlist",
    #"html_admonition",
    #"html_image",
    #"linkify",
    #"replacements",
    #"smartquotes",
    #"strikethrough",
    #"substitution",
    #"tasklist",
]

# autosectionlabel True to prefix each section label with the name of the document it is in, followed by a colon. 
# For example, index:Introduction for a section called Introduction that appears in document index.rst. Useful for 
# avoiding ambiguity when the same section heading appears in different documents.
autosectionlabel_prefix_document = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

templates_path = ['_templates']

# Some availble themes:
# 'agogo', 'basic', ' bizstyle', 'classic', 'default', 'epub', 'haiku', 'natura', 'nonav', 'pyramid', 'scrolls',
# 'sphinx doc', 'traditional'
# 'sphinxawesome_theme',
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = 'micat_logo.jpg'


# -- Options for PDF output -------------------------------------------------



# Grouping the document tree into PDF files. List of tuples
# (source start file, target name, title, author, options).
# Documentation of options: https://rst2pdf.org/static/manual.pdf
pdf_documents = [
    ('index', 'micat', ' ', author),
]

# A comma-separated list of custom stylesheets. Example:
pdf_stylesheets = ['sphinx', 'a4']

# Create compressed pdf
pdf_compressed = True

# A colon-separated list of folders to search for fonts. Example:
# pdf_font_path = ['/usr/share/fonts', '/usr/share/texmf-dist/fonts/']

# Language to be used for hyphenation support
pdf_language = "en_US"

# A list of folders to search for stylesheets. Example:
pdf_style_path = ['.', '_styles']

exclude_patterns = []

# Also see https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-latex-output

latex_logo = html_logo





