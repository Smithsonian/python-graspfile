# test_analysis_grid.py

import numpy as np
import pytest

from graspfile import grid
from graspfile.analysis import grid as ga

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
def filled_grasp_grid(empty_grasp_grid, grid_file):
    """Return a GraspGrid instance filled from the grid_file."""
    empty_grasp_grid.read(grid_file)
    grid_file.close()
    return empty_grasp_grid


@pytest.fixture
def filled_grasp_field(filled_grasp_grid):
    """Return a GraspField instance from the filled_grasp_grid fixture"""
    return filled_grasp_grid.fields[0]


def test_get_value(filled_grasp_field):
    """Test getting a value from the field"""
    x_vals, y_vals = filled_grasp_field.positions_1d

    # Test values of xv, yv in x_vals, y_vals
    xv = x_vals[int(len(x_vals)/3)]
    yv = y_vals[int(2*len(y_vals)/3)]

    value = filled_grasp_field.get_value(xv, yv)

    assert len(value) == filled_grasp_field.field_components

    # Test values of xv, yv not in x_vals, y_vals
    xv = (x_vals[int(len(x_vals)/3)] + x_vals[int(len(x_vals)/3)+1])/2
    yv = (y_vals[int(2*len(y_vals)/3)] + y_vals[int(2*len(y_vals)/3)-1])/2

    value = filled_grasp_field.get_value(xv, yv)

    assert len(value) == filled_grasp_field.field_components


def test_finding_peak(filled_grasp_field):
    """Test find the peak of a grasp field"""
    x_peak, y_peak = ga.find_peak(filled_grasp_field)

    assert x_peak >= filled_grasp_field.grid_min_x
    assert x_peak <= filled_grasp_field.grid_max_x
    assert y_peak >= filled_grasp_field.grid_min_y
    assert y_peak <= filled_grasp_field.grid_max_y


def test_finding_peak_comp1(filled_grasp_field):
    """Test find the peak of a grasp field"""
    x_peak, y_peak = ga.find_peak(filled_grasp_field, comp=1)

    assert x_peak >= filled_grasp_field.grid_min_x
    assert x_peak <= filled_grasp_field.grid_max_x
    assert y_peak >= filled_grasp_field.grid_min_y
    assert y_peak <= filled_grasp_field.grid_max_y


def test_finding_peak_min_radius(filled_grasp_field):
    """Test find the peak of a grasp field"""
    radii = filled_grasp_field.radius_grid()

    shape = radii.shape
    min_radius = radii[int(shape[0]/3), int(shape[1]/3)]

    x_peak, y_peak = ga.find_peak(filled_grasp_field, min_radius=min_radius)

    assert x_peak >= filled_grasp_field.grid_min_x
    assert x_peak <= filled_grasp_field.grid_max_x
    assert y_peak >= filled_grasp_field.grid_min_y
    assert y_peak <= filled_grasp_field.grid_max_y


def test_finding_peak_max_radius(filled_grasp_field):
    """Test find the peak of a grasp field"""
    radii = filled_grasp_field.radius_grid()

    shape = radii.shape
    max_radius = radii[int(shape[0] / 5), int(shape[1] / 5)]

    x_peak, y_peak = ga.find_peak(filled_grasp_field, max_radius=max_radius)

    assert x_peak >= filled_grasp_field.grid_min_x
    assert x_peak <= filled_grasp_field.grid_max_x
    assert y_peak >= filled_grasp_field.grid_min_y
    assert y_peak <= filled_grasp_field.grid_max_y


def test_finding_center(filled_grasp_field):
    """Test find the center of a grasp field"""
    x_cent, y_cent = ga.find_center(filled_grasp_field)

    assert x_cent >= filled_grasp_field.grid_min_x
    assert x_cent <= filled_grasp_field.grid_max_x
    assert y_cent >= filled_grasp_field.grid_min_y
    assert y_cent <= filled_grasp_field.grid_max_y


def test_finding_center_comp1(filled_grasp_field):
    """Test find the center of a grasp field"""
    x_cent, y_cent = ga.find_center(filled_grasp_field, comp=1)

    assert x_cent >= filled_grasp_field.grid_min_x
    assert x_cent <= filled_grasp_field.grid_max_x
    assert y_cent >= filled_grasp_field.grid_min_y
    assert y_cent <= filled_grasp_field.grid_max_y


def test_finding_center_trunc(filled_grasp_field):
    """Test find the center of a grasp field"""
    x_peak, y_peak = ga.find_peak(filled_grasp_field)
    peak = filled_grasp_field.get_value(x_peak, y_peak)

    trunc = np.abs(peak[0])/5.0

    x_cent, y_cent = ga.find_center(filled_grasp_field, trunc_level=trunc)

    assert x_cent >= filled_grasp_field.grid_min_x
    assert x_cent <= filled_grasp_field.grid_max_x
    assert y_cent >= filled_grasp_field.grid_min_y
    assert y_cent <= filled_grasp_field.grid_max_y


def test_finding_center_min_radius(filled_grasp_field):
    """Test find the center of a grasp field"""
    radii = filled_grasp_field.radius_grid()

    shape = radii.shape
    min_radius = radii[int(shape[0]/3), int(shape[1]/3)]

    x_cent, y_cent = ga.find_center(filled_grasp_field, min_radius=min_radius)

    assert x_cent >= filled_grasp_field.grid_min_x
    assert x_cent <= filled_grasp_field.grid_max_x
    assert y_cent >= filled_grasp_field.grid_min_y
    assert y_cent <= filled_grasp_field.grid_max_y


def test_finding_center_max_radius(filled_grasp_field):
    """Test find the center of a grasp field"""
    radii = filled_grasp_field.radius_grid()

    shape = radii.shape
    max_radius = radii[int(shape[0] / 5), int(shape[1] / 5)]

    x_cent, y_cent = ga.find_center(filled_grasp_field, max_radius=max_radius)

    assert x_cent >= filled_grasp_field.grid_min_x
    assert x_cent <= filled_grasp_field.grid_max_x
    assert y_cent >= filled_grasp_field.grid_min_y
    assert y_cent <= filled_grasp_field.grid_max_y
