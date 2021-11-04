========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |tests|
        | |codecov|
    * - package
      - | |commits-since|
.. |docs| image:: https://github.com/Smithsonian/python-graspfile/actions/workflows/build-docs.yml/badge.svg
    :alt: Doc Build Status
    :target: https://github.com/Smithsonian/python-graspfile/actions/workflows/build-docs.yml

.. |tests| image:: https://github.com/Smithsonian/python-graspfile/actions/workflows/test-with-tox.yml/badge.svg
    :alt: Test Status
    :target: https://github.com/Smithsonian/python-graspfile/actions/workflows/test-with-tox.yml

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
