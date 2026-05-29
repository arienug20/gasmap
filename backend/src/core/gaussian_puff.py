"""Gaussian Puff dispersion model (instantaneous release)."""

import numpy as np
from typing import Tuple, List, Dict

from .dispersion_coefficients import (
    get_sigma_y,
    get_sigma_z,
    get_sigma_y_vectorized,
    get_sigma_z_vectorized,
)
from .unit_converter import concentration_to_ppm


class GaussianPuff:
    """Gaussian Puff model for instantaneous release.

    C(x,y,z,t) = Q_total / ((2π)^1.5 · σx·σy·σz) ·
                  exp(-(x-ut)²/2σx²) · exp(-y²/2σy²) ·
                  [exp(-(z-H)²/2σz²) + exp(-(z+H)²/2σz²)]
    """

    def __init__(
        self,
        Q_total: float,
        u: float,
        H: float,
        stability: str,
        terrain: str = "rural",
        MW: float = 100.0,
    ):
        """Initialize Gaussian Puff model.

        Args:
            Q_total: Total mass released in kg
            u: Wind speed in m/s
            H: Release height in meters
            stability: Pasquill stability class A-F
            terrain: 'rural' or 'urban'
            MW: Molecular weight in g/mol
        """
        if u < 0:
            raise ValueError("Wind speed must be non-negative")
        if Q_total < 0:
            raise ValueError("Total mass must be non-negative")

        self.Q_total = Q_total  # kg
        self.u = u  # m/s
        self.H = H  # m
        self.stability = stability.upper()
        self.terrain = terrain
        self.MW = MW

        if self.stability not in "ABCDEF":
            raise ValueError(f"Invalid stability class: {stability}")

    def calculate_at_point_time(self, x: float, y: float, z: float, t: float) -> float:
        """Calculate concentration at a point and time.

        Args:
            x: Downwind position (m)
            y: Crosswind position (m)
            z: Height (m)
            t: Time since release (s)

        Returns:
            Concentration in ppm
        """
        if t <= 0 or self.Q_total == 0:
            return 0.0

        # Puff center travels with wind
        x_center = self.u * t
        x_eff = abs(x - x_center) + x_center  # effective travel distance for sigma

        if x_eff <= 0:
            return 0.0

        # Puff symmetry: σx = σy
        sigma_x = get_sigma_y(x_eff, self.stability, self.terrain)
        sigma_y = sigma_x  # puff symmetry
        sigma_z = get_sigma_z(x_eff, self.stability, self.terrain)

        C = (self.Q_total / ((2.0 * np.pi) ** 1.5 * sigma_x * sigma_y * sigma_z)) * \
            np.exp(-0.5 * ((x - x_center) / sigma_x) ** 2) * \
            np.exp(-0.5 * (y / sigma_y) ** 2) * \
            (np.exp(-0.5 * ((z - self.H) / sigma_z) ** 2) +
             np.exp(-0.5 * ((z + self.H) / sigma_z) ** 2))

        return concentration_to_ppm(C, self.MW)

    def calculate_time_series(
        self,
        x_range: Tuple[float, float] = (0, 5000),
        y_range: Tuple[float, float] = (-1000, 1000),
        z: float = 0.0,
        t_start: float = 1.0,
        t_end: float = 1000.0,
        n_steps: int = 50,
        resolution: int = 100,
    ) -> List[Tuple[float, np.ndarray]]:
        """Calculate time series of concentration grids.

        Returns:
            List of (time, concentration_grid_ppm) tuples
        """
        x = np.linspace(x_range[0], x_range[1], resolution)
        y = np.linspace(y_range[0], y_range[1], resolution)
        X, Y = np.meshgrid(x, y)

        times = np.linspace(t_start, t_end, n_steps)
        results = []

        for t in times:
            x_center = self.u * t
            # Effective distance for sigma
            X_eff = np.abs(X - x_center) + np.maximum(x_center, 1.0)

            sigma = get_sigma_y_vectorized(X_eff, self.stability, self.terrain)
            sigma_z = get_sigma_z_vectorized(X_eff, self.stability, self.terrain)

            C = np.where(
                sigma > 1e-10,
                (self.Q_total / ((2.0 * np.pi) ** 1.5 * sigma ** 2 * sigma_z)) *
                np.exp(-0.5 * ((X - x_center) / sigma) ** 2) *
                np.exp(-0.5 * (Y / sigma) ** 2) *
                (np.exp(-0.5 * ((z - self.H) / sigma_z) ** 2) +
                 np.exp(-0.5 * ((z + self.H) / sigma_z) ** 2)),
                0.0
            )

            C_ppm = np.vectorize(lambda c: concentration_to_ppm(c, self.MW))(C)
            C_ppm = np.maximum(C_ppm, 0.0)
            results.append((t, C_ppm))

        return results

    def get_max_concentration_envelope(
        self,
        x_range: Tuple[float, float] = (0, 5000),
        y_range: Tuple[float, float] = (-1000, 1000),
        z: float = 0.0,
        resolution: int = 100,
    ) -> np.ndarray:
        """Get maximum concentration at each grid point over all time.

        Returns:
            2D array of max concentration in ppm
        """
        t_end = (x_range[1] / max(self.u, 0.1)) * 2 if self.u > 0 else 1000
        results = self.calculate_time_series(
            x_range, y_range, z, t_start=1, t_end=t_end,
            n_steps=50, resolution=resolution,
        )

        envelope = np.zeros_like(results[0][1])
        for _, grid in results:
            envelope = np.maximum(envelope, grid)

        return envelope

    def get_time_of_arrival(self, x: float, threshold_ppm: float) -> float:
        """Find time when concentration first exceeds threshold at distance x.

        Args:
            x: Downwind distance (m)
            threshold_ppm: Threshold concentration in ppm

        Returns:
            Time in seconds, or -1 if never reached
        """
        if self.u <= 0:
            return -1.0

        t_arrival = x / self.u
        t_values = np.linspace(max(1, t_arrival * 0.1), t_arrival * 3, 1000)

        for t in t_values:
            c = self.calculate_at_point_time(x, 0.0, 0.0, t)
            if c >= threshold_ppm:
                return t

        return -1.0

    def get_duration_above_threshold(self, x: float, threshold_ppm: float) -> float:
        """Find duration concentration stays above threshold at distance x.

        Returns:
            Duration in seconds
        """
        if self.u <= 0:
            return 0.0

        t_arrival = x / max(self.u, 0.1)
        t_values = np.linspace(max(1, t_arrival * 0.1), t_arrival * 5, 2000)

        first_t = None
        last_t = None

        for t in t_values:
            c = self.calculate_at_point_time(x, 0.0, 0.0, t)
            if c >= threshold_ppm:
                if first_t is None:
                    first_t = t
                last_t = t

        if first_t is None:
            return 0.0
        return last_t - first_t
