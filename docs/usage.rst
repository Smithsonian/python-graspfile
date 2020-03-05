=====
Usage
=====

To use python-graspfile in a project::

	import graspfile

The graspfile module contains two main classes for reading GRASP output files, ``GraspGrid`` and ``GraspCut``, for
reading GRASP ``.grd`` and ``.cut`` files respectively.

In addition, there is a ``TorFile`` class, for reading and manipulating the ``.tor`` input files used by GRASP.
This class is still in development, and so should not be relied on to work, or to remain stable.
