"""Tests for Gaussian Puff dispersion model."""

import pytest
import numpy as np
from src.core.gaussian_puff import GaussianPuff


class TestGaussianPuff:
    """Gaussian Puff model tests."""

    def test_puff_center_travels_with_wind(self):
        """Puff center should travel at wind speed: x_center = u * t."""
        model = GaussianPuff(Q_total=100.0, u=5.0, H=0.0, stability="D", MW=100.0)
        # Max concentration at t=100s should be near x=500m
        c_at_500 = model.calculate_at_point_time(500, 0, 0, 100)
        c_at_200 = model.calculate_at_point_time(200, 0, 0, 100)
        assert c_at_500 > c_at_200, "Max should be near x=u*t"

    def test_zero_time_zero_concentration(self):
        """At t=0, concentration should be zero."""
        model = GaussianPuff(Q_total=100.0, u=5.0, H=0.0, stability="D", MW=100.0)
        c = model.calculate_at_point_time(0, 0, 0, 0)
        assert c == 0.0

    def test_zero_mass_zero_concentration(self):
        """With Q_total=0, concentration should be zero."""
        model = GaussianPuff(Q_total=0.0, u=5.0, H=0.0, stability="D", MW=100.0)
        c = model.calculate_at_point_time(500, 0, 0, 100)
        assert c == 0.0

    def test_stability_f_narrower_than_a(self):
        """Stability F puff should have higher peak (narrower) than A."""
        model_f = GaussianPuff(Q_total=100.0, u=5.0, H=0.0, stability="F", MW=100.0)
        model_a = GaussianPuff(Q_total=100.0, u=5.0, H=0.0, stability="A", MW=100.0)
        t = 50
        x_center = 5.0 * t
        c_f = model_f.calculate_at_point_time(x_center, 0, 0, t)
        c_a = model_a.calculate_at_point_time(x_center, 0, 0, t)
        # F is more stable → less spread → higher peak
        assert c_f > c_a, "Stability F should have higher peak than A"

    def test_concentration_rises_then_falls(self):
        """At a fixed point, concentration should rise then fall (unimodal)."""
        model = GaussianPuff(Q_total=100.0, u=5.0, H=0.0, stability="D", MW=100.0)
        x_obs = 500.0
        t_values = np.linspace(10, 300, 100)
        concs = [model.calculate_at_point_time(x_obs, 0, 0, t) for t in t_values]

        # Find peak
        peak_idx = np.argmax(concs)
        assert peak_idx > 0, "Peak should not be at start"
        assert peak_idx < len(concs) - 1, "Peak should not be at end"

    def test_time_series_produces_results(self):
        """Time series should produce multiple grids."""
        model = GaussianPuff(Q_total=100.0, u=5.0, H=0.0, stability="D", MW=100.0)
        results = model.calculate_time_series(
            x_range=(0, 2000), y_range=(-500, 500),
            t_start=10, t_end=200, n_steps=5, resolution=30,
        )
        assert len(results) == 5
        for t, grid in results:
            assert grid.shape == (30, 30)
            assert np.all(grid >= 0)
