import numpy as np
import pytest

from graspfile.analysis import reflectance


@pytest.fixture
def indices():
    """Return a list of refractive indices for testing."""
    return [1.0, 3.0, 1.0, 3.0, 1.0]


def test_reflectance():
    """Test single reflectance value"""
    r = reflectance.reflectance(1.0, 2.0)

    assert pytest.approx(r) == (1.0 - 2.0)/(1.0 + 2.0)


def test_transmittance():
    """Test single transmittance value"""
    t = reflectance.transmittance(1.0, 2.0)

    assert pytest.approx(t) == np.sqrt(1.0 - ((1.0 - 2.0)/(1.0 + 2.0))**2)


def test_total_transmittance(indices):
    """Test cascaded transmittance value"""
    t = reflectance.total_transmittance(indices)

    t_test = 1.0
    for i in range(len(indices)-1):
        t_test *= reflectance.transmittance(indices[i], indices[i+1])

    assert pytest.approx(t) == t_test
