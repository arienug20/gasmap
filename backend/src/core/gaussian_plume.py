"""Gaussian Plume dispersion model (Pasquill-Gifford)."""

import numpy as np
from typing import Tuple, Optional, Dict

from .dispersion_coefficients import (
    get_sigma_y,
    get_sigma_z,
    get_sigma_y_vectorized,
    get_sigma_z_vectorized,
)
from .unit_converter import concentration_to_ppm


class GaussianPlume:
    """Gaussian Plume model for continuous release.

    C(x,y,z) = Q / (2π·u·σy·σz) · exp(-y²/2σy²) ·
                [exp(-(z-H)²/2σz²) + exp(-(z+H)²/2σz²)]
    """

    def __init__(
        self,
        Q: float,
        u: float,
        H: float,
        stability: str,
        terrain: str = "rural",
        MW: float = 100.0,
    ):
        """Initialize Gaussian Plume model.

        Args:
            Q: Emission rate in kg/s
            u: Wind speed in m/s (must be > 0)
            H: Effective release height in meters
            stability: Pasquill stability class A-F
            terrain: 'rural' or 'urban'
            MW: Molecular weight in g/mol (for ppm conversion)
        """
        if u <= 0:
            raise ValueError("Wind speed must be greater than 0")
        if Q < 0:
            raise ValueError("Emission rate must be non-negative")

        self.Q = Q  # kg/s
        self.u = u  # m/s
        self.H = H  # m
        self.stability = stability.upper()
        self.terrain = terrain
        self.MW = MW

        if self.stability not in "ABCDEF":
            raise ValueError(f"Invalid stability class: {stability}")

    def get_sigma_y(self, x: float) -> float:
        """Get lateral dispersion coefficient at distance x."""
        return get_sigma_y(x, self.stability, self.terrain)

    def get_sigma_z(self, x: float) -> float:
        """Get vertical dispersion coefficient at distance x."""
        return get_sigma_z(x, self.stability, self.terrain)

    def calculate_at_point(self, x: float, y: float, z: float = 0.0) -> float:
        """Calculate concentration at a single point in ppm.

        Args:
            x: Downwind distance (m)
            y: Crosswind distance (m)
            z: Height above ground (m)

        Returns:
            Concentration in ppm
        """
        if x <= 0:
            return 0.0

        sy = self.get_sigma_y(x)
        sz = self.get_sigma_z(x)

        # Concentration in kg/m³
        C = (self.Q / (2.0 * np.pi * self.u * sy * sz)) * \
            np.exp(-0.5 * (y / sy) ** 2) * \
            (np.exp(-0.5 * ((z - self.H) / sz) ** 2) +
             np.exp(-0.5 * ((z + self.H) / sz) ** 2))

        return concentration_to_ppm(C, self.MW)

    def calculate_concentration_grid(
        self,
        x_range: Tuple[float, float] = (10, 5000),
        y_range: Tuple[float, float] = (-1000, 1000),
        z: float = 0.0,
        resolution: int = 200,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculate concentration on a 2D grid.

        Returns:
            Tuple of (X grid, Y grid, concentration in ppm)
        """
        x = np.linspace(x_range[0], max(x_range[1], x_range[0] + 1), resolution)
        y = np.linspace(y_range[0], y_range[1], resolution)
        X, Y = np.meshgrid(x, y)

        # Vectorized sigma calculations
        sy = get_sigma_y_vectorized(X, self.stability, self.terrain)
        sz = get_sigma_z_vectorized(X, self.stability, self.terrain)

        # Gaussian plume formula (concentration in kg/m³)
        C = (self.Q / (2.0 * np.pi * self.u * sy * sz)) * \
            np.exp(-0.5 * (Y / sy) ** 2) * \
            (np.exp(-0.5 * ((z - self.H) / sz) ** 2) +
             np.exp(-0.5 * ((z + self.H) / sz) ** 2))

        # Convert to ppm
        C_ppm = np.vectorize(lambda c: concentration_to_ppm(c, self.MW))(C)
        C_ppm = np.maximum(C_ppm, 0.0)

        return X, Y, C_ppm

    def get_max_ground_concentration(self) -> Tuple[float, float]:
        """Find maximum ground-level centerline concentration and its distance.

        Returns:
            Tuple of (C_max in ppm, x_max in meters)
        """
        x_values = np.linspace(10, 10000, 1000)
        max_c = 0.0
        x_max = 10.0

        for x in x_values:
            c = self.calculate_at_point(x, 0.0, 0.0)
            if c > max_c:
                max_c = c
                x_max = x

        return max_c, x_max

    def get_threshold_distances(
        self, threshold_ppm: float, z: float = 0.0
    ) -> Dict[str, float]:
        """Find downwind distances where concentration equals threshold.

        Returns:
            Dict with 'near' and 'far' distances in meters
        """
        x_values = np.linspace(1, 50000, 5000)
        centerline = np.array([self.calculate_at_point(x, 0.0, z) for x in x_values])

        # Find crossings
        above = centerline >= threshold_ppm
        crossings = []

        for i in range(1, len(above)):
            if above[i] != above[i - 1]:
                # Linear interpolation
                x_cross = x_values[i - 1] + (threshold_ppm - centerline[i - 1]) / \
                          (centerline[i] - centerline[i - 1]) * \
                          (x_values[i] - x_values[i - 1])
                crossings.append(x_cross)

        result = {"near": 0.0, "far": 0.0}
        if len(crossings) >= 2:
            result["near"] = crossings[0]
            result["far"] = crossings[-1]
        elif len(crossings) == 1:
            result["near"] = crossings[0]

        return result

    def get_crosswind_profile(self, x: float, z: float = 0.0) -> np.ndarray:
        """Get concentration profile across the wind at distance x.

        Returns:
            Array of concentrations in ppm for y from -3σy to +3σy
        """
        sy = self.get_sigma_y(x)
        y_values = np.linspace(-3 * sy, 3 * sy, 100)
        concentrations = np.array([self.calculate_at_point(x, y, z) for y in y_values])
        return concentrations

    def get_vertical_profile(self, x: float, y: float = 0.0) -> np.ndarray:
        """Get vertical concentration profile at distance x and offset y."""
        z_values = np.linspace(0, 200, 100)
        concentrations = np.array([self.calculate_at_point(x, y, z) for z in z_values])
        return concentrations

    def get_plume_rise(self, Vs: float, d: float, Ts: float, Ta: float = 293.0) -> float:
        """Calculate Briggs plume rise (buoyancy-dominated, neutral conditions).

        Args:
            Vs: Stack gas exit velocity (m/s)
            d: Stack inner diameter (m)
            Ts: Stack gas temperature (K)
            Ta: Ambient temperature (K)

        Returns:
            Plume rise Δh in meters
        """
        g = 9.81
        F = g * Vs * d ** 2 * (Ts - Ta) / (4.0 * Ts)  # Buoyancy flux
        # Buoyancy-dominated, neutral: Δh = 1.6 * F^(1/3) * x^(2/3) / u
        # At final rise distance x_f ≈ 3.5 * x* where x* = 14 * F^(5/8) for F < 55
        if F < 55:
            x_star = 14.0 * F ** 0.625
        else:
            x_star = 34.0 * F ** 0.4
        x_f = 3.5 * x_star

        delta_h = 1.6 * F ** (1.0 / 3.0) * x_f ** (2.0 / 3.0) / self.u
        return delta_h
