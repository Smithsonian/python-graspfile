# test_cut.py

import pytest
from pytest import approx

from graspfile import cut

test_cut_file = "tests/test_data/grasp_files/cut_files/example_GRASP_10-0-1_spherical_polar_linear_farfield.cut"
"""TICRA Tools 19.1 GRASP Cut file"""


@pytest.fixture
def empty_grasp_cutfile():
    """Return an empty  instance."""
    return cut.GraspCut()


@pytest.fixture
def cut_file():
    """Return a file object that points to a GRASP Cut file"""
    return open(test_cut_file)


@pytest.fixture
def filled_grasp_cut_file(empty_grasp_cutfile, cut_file):
    """Return a GraspCutFile instance filled from the cut_file."""
    empty_grasp_cutfile.read(cut_file)
    cut_file.close()
    return empty_grasp_cutfile


@pytest.fixture
def filled_grasp_cut(filled_grasp_cut_file):
    """Return a GraspField instance from the filled_grasp_grid fixture"""
    return filled_grasp_cut_file.cut_sets[0].cuts[0]


def test_loading_cut_file(filled_grasp_cut_file):
    """Test loading cut from a TICRA Cut file."""
    # check that enough frequencies and fields were read
    assert len(filled_grasp_cut_file.cut_sets[0].cuts) > 0

    # Check that parameters were read correctly
    assert filled_grasp_cut_file.cut_type in ["spherical", "planar", "cylindrical"]
    assert len(filled_grasp_cut_file.constants) > 0


def test_select_pos_range_file(filled_grasp_cut_file):
    """Check that returning a sub range works"""
    filled_grasp_cut = filled_grasp_cut_file.cut_sets[0].cuts[0]

    v_min = filled_grasp_cut.v_ini
    v_max = filled_grasp_cut.v_ini + \
        (filled_grasp_cut.v_num - 1) * filled_grasp_cut.v_inc
    v_cent = (v_min + v_max) / 2.0
    v_range = (v_max - v_min) / 2

    pos_max = v_cent + v_range / 2
    pos_min = v_cent - v_range / 2

    newcf = filled_grasp_cut_file.select_pos_range(pos_min, pos_max)

    assert len(newcf.cut_sets) == len(filled_grasp_cut_file.cut_sets)
    assert len(newcf.cut_sets[0].cuts) == len(filled_grasp_cut_file.cut_sets[0].cuts)


def test_loading_cut(filled_grasp_cut):
    """Test the individual field loaded as part of filled_grasp_grid"""
    # check that cut parameters were filled correctly

    assert type(filled_grasp_cut.v_ini) is float
    assert type(filled_grasp_cut.v_inc) is float
    assert type(filled_grasp_cut.v_num) is int

    assert filled_grasp_cut.cut_type in range(1, 4)
    assert type(filled_grasp_cut.constant) is float
    assert filled_grasp_cut.icut in range(1, 3)
    assert filled_grasp_cut.polarization in range(1, 10)
    assert filled_grasp_cut.field_components in [2, 3]

    # Check that the shape of the field is consistent with grid parameters
    data_shape = filled_grasp_cut.data.shape

    assert data_shape[0] == filled_grasp_cut.v_num
    assert data_shape[1] == filled_grasp_cut.field_components
