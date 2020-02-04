========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |requires|
        | |codecov|
    * - package
      - | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/python-graspfile/badge/?style=flat
    :target: https://readthedocs.org/projects/python-graspfile
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.org/paulkgrimes/python-graspfile.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/paulkgrimes/python-graspfile

.. |requires| image:: https://requires.io/github/paulkgrimes/python-graspfile/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/paulkgrimes/python-graspfile/requirements/?branch=master

.. |codecov| image:: https://codecov.io/github/paulkgrimes/python-graspfile/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/paulkgrimes/python-graspfile

.. |commits-since| image:: https://img.shields.io/github/commits-since/paulkgrimes/python-graspfile/v0.0.1.svg
    :alt: Commits since latest release
    :target: https://github.com/paulkgrimes/python-graspfile/compare/v0.0.1...master



.. end-badges

A package for reading, manipulating and eventually writing files output from TICRA Tools GRASP and CHAMP software using
numpy etc.

* Free software: MIT license

Installation
============

::

    pip install python-graspfile

You can also install the in-development version with::

    pip install https://github.com/paulkgrimes/python-graspfile/archive/master.zip


Documentation
=============


https://python-graspfile.readthedocs.io/


Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
