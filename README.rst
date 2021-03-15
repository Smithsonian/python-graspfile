========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis|
        | |codecov|
    * - package
      - | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/python-graspfile/badge/?style=flat
    :target: https://readthedocs.org/projects/python-graspfile
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.org/Smithsonian/python-graspfile.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/Smithsonian/python-graspfile

.. |codecov| image:: https://codecov.io/github/Smithsonian/python-graspfile/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/Smithsonian/python-graspfile

.. |commits-since| image:: https://img.shields.io/github/commits-since/Smithsonian/python-graspfile/v0.4.0.svg
    :alt: Commits since latest release
    :target: https://github.com/Smithsonian/python-graspfile/compare/v0.4.0...master



.. end-badges

A package for reading, manipulating and eventually writing files output from TICRA Tools GRASP and CHAMP software using
numpy etc.

* Free software: MIT license

Installation
============

::

    pip install python-graspfile

You can also install the latest release candidate version with::

    pip install --index-url https://test.pypi.org/simple/ python-graspfile

You can install the latest in-development version with::

    pip install https://github.com/Smithsonian/python-graspfile/archive/master.zip


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

