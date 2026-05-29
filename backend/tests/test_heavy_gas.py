"""Tests for Heavy Gas (Britter-McQuaid) model."""

import pytest
from src.core.heavy_gas_bm import HeavyGasBM


class TestHeavyGas:
    """Heavy Gas Britter-McQuaid model tests."""

    def test_chlorine_is_heavy_gas(self):
        """Chlorine (ρ=3.21 kg/m³) should be classified as heavy gas."""
        model = HeavyGasBM(Q=1.0, rho_release=3.21, u=5.0, H=0.0, MW=70.9)
        assert model.is_heavy_gas() is True

    def test_light_gas_not_heavy(self):
        """Gas with density close to air should not be heavy gas."""
        model = HeavyGasBM(Q=1.0, rho_release=1.1, u=5.0, H=0.0, MW=28.0)
        assert model.is_heavy_gas() is False

    def test_richardson_number_positive(self):
        """Richardson number should be positive for heavy gas."""
        model = HeavyGasBM(Q=1.0, rho_release=3.21, u=5.0, H=0.0, MW=70.9)
        ri = model.get_richardson_number()
        assert ri > 0, "Ri should be positive for heavy gas"

    def test_zero_wind_raises_error(self):
        """Zero wind should raise ValueError."""
        with pytest.raises(ValueError):
            HeavyGasBM(Q=1.0, rho_release=3.21, u=0.0, H=0.0, MW=70.9)

    def test_negative_density_raises_error(self):
        """Negative density should raise ValueError."""
        with pytest.raises(ValueError):
            HeavyGasBM(Q=1.0, rho_release=-1.0, u=5.0, H=0.0, MW=70.9)

    def test_concentration_decreases_with_distance(self):
        """Central concentration should decrease with distance."""
        model = HeavyGasBM(Q=1.0, rho_release=3.21, u=5.0, H=0.0, MW=70.9)
        c_near = model.get_central_concentration(100)
        c_far = model.get_central_concentration(1000)
        assert c_near > c_far, "Concentration should decrease with distance"

    def test_cloud_half_width_increases(self):
        """Cloud half-width should increase with distance."""
        model = HeavyGasBM(Q=1.0, rho_release=3.21, u=5.0, H=0.0, MW=70.9)
        w_near = model.get_cloud_half_width(100)
        w_far = model.get_cloud_half_width(1000)
        assert w_far > w_near, "Half-width should increase"

    def test_transition_distance_positive(self):
        """Transition distance should be positive."""
        model = HeavyGasBM(Q=1.0, rho_release=3.21, u=5.0, H=0.0, MW=70.9)
        x_trans = model.get_transition_distance()
        assert x_trans > 0, "Transition distance should be positive"

    def test_high_wind_small_richardson(self):
        """Higher wind speed should produce smaller Richardson number."""
        model_low = HeavyGasBM(Q=1.0, rho_release=3.21, u=2.0, H=0.0, MW=70.9)
        model_high = HeavyGasBM(Q=1.0, rho_release=3.21, u=10.0, H=0.0, MW=70.9)
        assert model_high.get_richardson_number() < model_low.get_richardson_number()
