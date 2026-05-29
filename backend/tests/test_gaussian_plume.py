"""Tests for Gaussian Plume dispersion model."""

import pytest
import numpy as np
from src.core.gaussian_plume import GaussianPlume
from src.core.dispersion_coefficients import get_sigma_y, get_sigma_z


class TestGaussianPlume:
    """Gaussian Plume model tests."""

    def test_zero_wind_raises_error(self):
        """Zero wind speed should raise ValueError."""
        with pytest.raises(ValueError, match="Wind speed"):
            GaussianPlume(Q=1.0, u=0.0, H=0.0, stability="D")

    def test_negative_wind_raises_error(self):
        """Negative wind speed should raise ValueError."""
        with pytest.raises(ValueError):
            GaussianPlume(Q=1.0, u=-1.0, H=0.0, stability="D")

    def test_negative_emission_raises_error(self):
        """Negative emission rate should raise ValueError."""
        with pytest.raises(ValueError):
            GaussianPlume(Q=-1.0, u=5.0, H=0.0, stability="D")

    def test_invalid_stability_raises_error(self):
        """Invalid stability class should raise ValueError."""
        with pytest.raises(ValueError):
            GaussianPlume(Q=1.0, u=5.0, H=0.0, stability="X")

    def test_centerline_concentration_positive(self):
        """Centerline concentration should be positive for valid input."""
        model = GaussianPlume(Q=10.0, u=5.0, H=0.0, stability="D", MW=70.9)
        c = model.calculate_at_point(100, 0, 0)
        assert c > 0, "Centerline concentration should be positive"

    def test_concentration_decreases_with_distance(self):
        """Ground-level centerline concentration decreases with distance (H=0)."""
        model = GaussianPlume(Q=10.0, u=5.0, H=0.0, stability="D", MW=100.0)
        c100 = model.calculate_at_point(100, 0, 0)
        c500 = model.calculate_at_point(500, 0, 0)
        c1000 = model.calculate_at_point(1000, 0, 0)
        assert c100 > c500 > c1000, "Concentration should decrease with distance"

    def test_off_centerline_less_than_centerline(self):
        """Off-centerline concentration should be less than centerline."""
        model = GaussianPlume(Q=10.0, u=5.0, H=0.0, stability="D", MW=100.0)
        c_center = model.calculate_at_point(500, 0, 0)
        c_off = model.calculate_at_point(500, 50, 0)
        assert c_off < c_center, "Off-centerline should be less"

    def test_elevated_release_lower_ground_conc(self):
        """Elevated release should have lower ground-level concentration at close range."""
        model_ground = GaussianPlume(Q=10.0, u=5.0, H=0.0, stability="D", MW=100.0)
        model_elevated = GaussianPlume(Q=10.0, u=5.0, H=50.0, stability="D", MW=100.0)
        c_ground = model_ground.calculate_at_point(100, 0, 0)
        c_elevated = model_elevated.calculate_at_point(100, 0, 0)
        assert c_elevated < c_ground, "Elevated should have lower ground conc at x=100"

    def test_negative_x_zero_concentration(self):
        """Negative x should return zero concentration."""
        model = GaussianPlume(Q=10.0, u=5.0, H=0.0, stability="D", MW=100.0)
        c = model.calculate_at_point(-100, 0, 0)
        assert c == 0.0, "Negative x should give zero"

    def test_zero_x_zero_concentration(self):
        """x=0 should return zero concentration."""
        model = GaussianPlume(Q=10.0, u=5.0, H=0.0, stability="D", MW=100.0)
        c = model.calculate_at_point(0, 0, 0)
        assert c == 0.0, "x=0 should give zero"

    def test_grid_computation_shape(self):
        """Grid computation should return correct shape."""
        model = GaussianPlume(Q=10.0, u=5.0, H=0.0, stability="D", MW=100.0)
        X, Y, C = model.calculate_concentration_grid(resolution=50)
        assert C.shape == (50, 50), f"Expected (50,50), got {C.shape}"

    def test_grid_non_negative(self):
        """All grid values should be non-negative."""
        model = GaussianPlume(Q=10.0, u=5.0, H=0.0, stability="D", MW=100.0)
        _, _, C = model.calculate_concentration_grid(resolution=50)
        assert np.all(C >= 0), "Concentrations should be non-negative"

    def test_sigma_y_monotonic_increase(self):
        """σy should increase monotonically with distance."""
        x_values = [100, 500, 1000, 5000]
        sy_values = [get_sigma_y(x, "D") for x in x_values]
        for i in range(len(sy_values) - 1):
            assert sy_values[i] < sy_values[i + 1], f"σy not monotonic at x={x_values[i]}"

    def test_sigma_z_monotonic_increase(self):
        """σz should increase monotonically with distance (for classes A-D)."""
        x_values = [100, 500, 1000, 5000]
        sz_values = [get_sigma_z(x, "C") for x in x_values]
        for i in range(len(sz_values) - 1):
            assert sz_values[i] < sz_values[i + 1], f"σz not monotonic at x={x_values[i]}"

    def test_stability_a_more_spread_than_f(self):
        """Stability A should have larger σy than F at same distance."""
        sy_a = get_sigma_y(1000, "A")
        sy_f = get_sigma_y(1000, "F")
        assert sy_a > sy_f, "Stability A should spread more than F"

    def test_max_ground_concentration_found(self):
        """get_max_ground_concentration should return positive values."""
        model = GaussianPlume(Q=10.0, u=5.0, H=0.0, stability="D", MW=100.0)
        c_max, x_max = model.get_max_ground_concentration()
        assert c_max > 0, "Max concentration should be positive"
        assert x_max > 0, "Max distance should be positive"

    def test_urban_vs_rural_sigma(self):
        """Urban σ should differ from rural."""
        sy_rural = get_sigma_y(1000, "D", "rural")
        sy_urban = get_sigma_y(1000, "D", "urban")
        assert sy_rural != sy_urban, "Urban and rural σy should differ"

    def test_threshold_distances_for_zero_height(self):
        """Threshold distances should be found for ground-level release."""
        model = GaussianPlume(Q=100.0, u=3.0, H=0.0, stability="F", MW=70.9)
        result = model.get_threshold_distances(10.0)
        # For large Q with stable conditions, threshold should be reached
        assert result["far"] > 0 or result["near"] > 0
