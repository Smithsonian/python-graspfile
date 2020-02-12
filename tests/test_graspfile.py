# test_graspfile.py

import pytest

from graspfile import cut, cutfile, grid

test_grid_file = "test_data/grasp_files/square_aperture_7-47mm_square_82-97-112GHz.grd"
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
    """Return an empty GraspGrid instance."""
    empty_grasp_grid.read_grasp_grid(grid_file)
    grid_file.close()
    return empty_grasp_grid


def test_loading_grid(filled_grasp_grid):
    """Test loading grid from a TICRA Grid file."""
    # check that enough freqs and fields were read
    assert len(filled_grasp_grid.freqs) == 3
    assert len(filled_grasp_grid.fields) == 3

    # Check that parameters were read correctly
    assert filled_grasp_grid.ktype == 1
    assert filled_grasp_grid.nset == 3
    assert filled_grasp_grid.icomp == 3
    assert filled_grasp_grid.ncomp == 3
    assert filled_grasp_grid.igrid == 3

    # Check that beam centers were read correctly
    assert len(filled_grasp_grid.beam_centers) == 3
    for bc in filled_grasp_grid.beam_centers:
        assert bc == [0, 0]
