# test_file.py

import io

import pytest

import graspfile.torfile

test_file = "tests/test_data/tor_files/python-graspfile-example.tor"
"""TICRA Tools 10.0.1 GRASP .tor file"""


@pytest.fixture
def empty_tor_file():
    """Return an empty GraspTorFile instance."""
    return graspfile.torfile.GraspTorFile()


@pytest.fixture
def input_file_object():
    """Return a file object pointing to the test file."""
    return open(test_file)


@pytest.fixture
def filled_tor_file(empty_tor_file, input_file_object):
    """Return a GraspTorFile instance filled from the tor_file"""
    empty_tor_file.read(input_file_object)
    input_file_object.close()
    return empty_tor_file


def test_loading_tor_file(filled_tor_file):
    """Test loading from a tor cutfile"""
    # Check that something was loaded
    assert len(filled_tor_file.keys()) > 0

    # Check that the frequencies were loaded
    assert len(filled_tor_file["single_frequencies"].keys()) > 0


def test_reloading_tor_file(filled_tor_file):
    """Test outputting the filled_tor_file to text and reloading it with StringIO"""
    test_str = repr(filled_tor_file)

    try:
        test_io = io.StringIO(test_str)
    except TypeError:
        test_io = io.StringIO(unicode(test_str))

    reload_tor_file = graspfile.torfile.GraspTorFile(test_io)

    assert len(filled_tor_file.keys()) == len(reload_tor_file.keys())
