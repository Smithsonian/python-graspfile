# test_grid.py

import pytest
from pytest import approx

from graspfile import grid

test_grid_file = "tests/test_data/grasp_files/square_aperture.grd"
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
def write_filename():
    """Return a file name for test writing and reading back"""
    return "temp.grd"

@pytest.fixture
def filled_grasp_grid(empty_grasp_grid, grid_file):
    """Return a GraspGrid instance filled from the grid_file."""
    empty_grasp_grid.read(grid_file)
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
    assert filled_grasp_grid.polarization in range(1, 12)
    assert filled_grasp_grid.field_components in [2, 3]
    assert filled_grasp_grid.igrid in [2, 3, 8]

    # Check that beam centers were read correctly
    assert len(filled_grasp_grid.beam_centers) > 0
    for bc in filled_grasp_grid.beam_centers:
        assert len(bc) == 2


def test_rotate_grid_polarization(filled_grasp_grid):
    """Check that rotate_polarization runs on all fields"""
    filled_grasp_grid.rotate_polarization()
    filled_grasp_grid.rotate_polarization(angle=-45.0)


def test_loading_field(filled_grasp_field):
    """Test the individual field loaded as part of filled_grasp_grid"""
    # check that field parameters were filled correctly
    assert type(filled_grasp_field.beam_center[0]) is int
    assert type(filled_grasp_field.beam_center[1]) is int
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
    assert filled_grasp_field.grid_step_x == approx(
        (filled_grasp_field.grid_max_x - filled_grasp_field.grid_min_x) / (filled_grasp_field.grid_n_x - 1))
    assert filled_grasp_field.grid_step_y == approx((filled_grasp_field.grid_max_y - filled_grasp_field.grid_min_y) / (
        filled_grasp_field.grid_n_y - 1))

    assert filled_grasp_field.k_limit in [0, 1]
    assert filled_grasp_field.field_components in [2, 3]

    # Check that the shape of the field is consistent with grid parameters
    field_shape = filled_grasp_field.field.shape

    assert field_shape[0] == filled_grasp_field.grid_n_x
    assert field_shape[1] == filled_grasp_field.grid_n_y
    assert field_shape[2] == filled_grasp_field.field_components


def test_writing_grid(filled_grasp_grid, tmp_path, write_filename):
    """Test writing of filled grid to file, and then reading it back"""
    filename = tmp_path / write_filename
    fo = open(filename, "w")
    filled_grasp_grid.write(fo)
    fo.close()

    fi = open(filename, "r")
    saved_grid = grid.GraspGrid()
    saved_grid.read(fi)
    fi.close()

    # Check that all the freqs and fields were read
    assert len(filled_grasp_grid.freqs) == len(saved_grid.freqs)
    assert len(filled_grasp_grid.fields) == len(saved_grid.fields)

    # Check that parameters were read correctly
    assert filled_grasp_grid.ktype == saved_grid.ktype
    assert filled_grasp_grid.nset == saved_grid.nset
    assert filled_grasp_grid.polarization == saved_grid.polarization
    assert filled_grasp_grid.field_components == saved_grid.field_components
    assert filled_grasp_grid.igrid == saved_grid.igrid


def test_index_radial_dist(filled_grasp_field):
    """Test the return of an array of radial distances of grid points"""
    rdist = filled_grasp_field.index_radial_dist(3, 2)
    assert rdist >= 0.0


def test_grid_pos(filled_grasp_field):
    """Test the return of the meshed grid of positions"""
    xgrid, ygrid = filled_grasp_field.positions

    assert xgrid.shape == (filled_grasp_field.grid_n_x, filled_grasp_field.grid_n_y)
    assert ygrid.shape == (filled_grasp_field.grid_n_x, filled_grasp_field.grid_n_y)


def test_radius_grid(filled_grasp_field):
    rgrid = filled_grasp_field.radius_grid()

    assert rgrid.shape == (filled_grasp_field.grid_n_x, filled_grasp_field.grid_n_y)

    rgrid2 = filled_grasp_field.radius_grid((0.1, 0.1))

    assert rgrid2.shape == (filled_grasp_field.grid_n_x, filled_grasp_field.grid_n_y)


def test_rotate_polarization(filled_grasp_field):
    ang = 180.0

    rot_field = filled_grasp_field

    rot_field.rotate_polarization(ang)
    rot_field.rotate_polarization(ang)

    assert rot_field.field == approx(filled_grasp_field.field)


def test_combine_grid(filled_grasp_grid):
    comb_field = filled_grasp_grid

    comb_field.combine_fields(coherent=False)

    assert len(comb_field.fields) == 1
    assert len(comb_field.freqs) == 1


def test_combine_grid_coherent(filled_grasp_grid):
    comb_field = filled_grasp_grid

    comb_field.combine_fields(coherent=True)

    assert len(comb_field.fields) == 1


def test_scale_field(filled_grasp_field):
    filled_grasp_field.scale_field(2.0)


def test_scale_grid(filled_grasp_grid):
    filled_grasp_grid.scale_fields(2.0)

