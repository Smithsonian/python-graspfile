# test_graspfile.py
import os
import pytest
from pytest import approx

from graspfile import grid


test_grid_file = "tests/test_data/grasp_files/square_aperture_7-47mm_square_82-97-112GHz.grd"
"""TICRA Tools 19.1 GRASP Grid file, consisting of three grids at 82, 97 and 112 GHz."""


@pytest.fixture
def empty_grasp_grid():
    """Return an empty GraspGrid instance."""
    return grid.GraspGrid()


@pytest.fixture
def grid_file():
    """Return a file object that points to a GRASP Grid file"""
    return open(test_grid_file)


@pytest.fixture
def filled_grasp_grid(empty_grasp_grid, grid_file):
    """Return a GraspGrid instance filled from the grid_file."""
    empty_grasp_grid.read_grasp_grid(grid_file)
    grid_file.close()
    return empty_grasp_grid


@pytest.fixture
def filled_grasp_field(filled_grasp_grid):
    """Return a GraspField instance from the filled_grasp_grid fixture"""
    return filled_grasp_grid.fields[0]


def test_loading_grid(filled_grasp_grid):
    """Test loading grid from a TICRA Grid file."""
    # check that enough freqs and fields were read
    assert len(filled_grasp_grid.freqs) > 0
    assert len(filled_grasp_grid.fields) > 0

    # Check that parameters were read correctly
    assert filled_grasp_grid.ktype in [1]
    assert type(filled_grasp_grid.nset) is int
    assert filled_grasp_grid.icomp in [1,2,3]
    assert filled_grasp_grid.ncomp in [2,3]
    assert filled_grasp_grid.igrid in [1,2,3]

    # Check that beam centers were read correctly
    assert len(filled_grasp_grid.beam_centers) == 3
    for bc in filled_grasp_grid.beam_centers:
        assert len(bc) == 2


def test_loading_field(filled_grasp_field):
    """Test the individual field loaded as part of filled_grasp_grid"""
    # check that field parameters were filled correctly
    assert type(filled_grasp_field.beam_center[0]) is float
    assert type(filled_grasp_field.beam_center[1]) is float
    assert len(filled_grasp_field.beam_center) == 2

    assert type(filled_grasp_field.grid_min_x) is float
    assert type(filled_grasp_field.grid_min_y) is float
    assert type(filled_grasp_field.grid_max_x) is float
    assert type(filled_grasp_field.grid_max_y) is float
    assert type(filled_grasp_field.grid_n_x) is int
    assert type(filled_grasp_field.grid_n_y) is int
    assert type(filled_grasp_field.grid_step_x) is float
    assert type(filled_grasp_field.grid_step_y) is float

    # Check that the step values are consistent with the other grid parameters
    # (should find and use the "approx equal" test)
    assert filled_grasp_field.grid_step_x == approx((filled_grasp_field.grid_max_x - filled_grasp_field.grid_min_x)/(filled_grasp_field.grid_n_x - 1))
    assert filled_grasp_field.grid_step_y == approx((filled_grasp_field.grid_max_y - filled_grasp_field.grid_min_y) / (
            filled_grasp_field.grid_n_y - 1))

    assert filled_grasp_field.k_limit in [0, 1]
    assert filled_grasp_field.ncomp in [2, 3]

    # Check that the shape of the field is consistent with grid parameters
    field_shape = filled_grasp_field.field.shape

    assert field_shape[0] == filled_grasp_field.grid_n_x
    assert field_shape[1] == filled_grasp_field.grid_n_y
    assert field_shape[2] == filled_grasp_field.ncomp



