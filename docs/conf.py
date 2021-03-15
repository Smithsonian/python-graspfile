# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
sys.path.insert(0, os.path.abspath('..'))
import sphinx_rtd_theme

# -- General configuration ------------------------------------------------
autoclass_content = "both"  # include both class docstring and __init__
autodoc_default_flags = [
        # Make sure that any autodoc declarations show the right members
        "members",
        "inherited-members",
        "private-members",
        "show-inheritance",
]
autosummary_generate = True  # Make _autosummary files and include them
napoleon_numpy_docstring = False  # Force consistency, leave only Google
napoleon_use_rtype = False  # More legible

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx_automodapi.automodapi',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.extlinks',
    'sphinx.ext.ifconfig',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
]
numpydoc_show_class_members = False
source_suffix = '.rst'
master_doc = 'index'
project = 'python-graspfile'
year = '2019-2020'
author = 'Paul Grimes'
copyright = '{0}, {1}'.format(year, author)
version = release = '0.4.0'

pygments_style = 'trac'
templates_path = ['.']
extlinks = {
    'issue': ('https://github.com/Smithsonian/python-graspfile/issues/%s', '#'),
    'pr': ('https://github.com/Smithsonian/python-graspfile/pull/%s', 'PR #'),
}


html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme_options = {
}

html_use_smartypants = True
html_last_updated_fmt = '%b %d, %Y'
html_split_index = False
html_sidebars = {
    '**': ['searchbox.html', 'globaltoc.html', 'sourcelink.html'],
}
html_short_title = '%s-%s' % (project, version)

napoleon_use_ivar = True
napoleon_use_rtype = False
napoleon_use_param = False
