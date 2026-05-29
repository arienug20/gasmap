"""Heavy Gas dispersion model (Britter-McQuaid simplified)."""

import numpy as np
from typing import Tuple, Dict, Optional

from .unit_converter import concentration_to_ppm, ppm_to_kgm3


class HeavyGasBM:
    """Britter-McQuaid dense gas dispersion model.

    Uses dimensionless analysis with Richardson number and
    digitized nomogram correlations.
    """

    # Air properties
    RHO_AIR = 1.225  # kg/m³ at sea level, 15°C
    G = 9.81  # m/s²

    # Britter-McQuaid nomogram data points (digitized)
    # Format: (x/D, C/C0) for different Richardson numbers
    # These are approximate correlations from B&M (1988) figures
    _NOMOGRAM_RI_10 = [
        (1, 0.95), (5, 0.75), (10, 0.62), (20, 0.48),
        (50, 0.32), (100, 0.22), (200, 0.14), (500, 0.07),
    ]
    _NOMOGRAM_RI_100 = [
        (1, 0.98), (5, 0.90), (10, 0.82), (20, 0.70),
        (50, 0.52), (100, 0.38), (200, 0.25), (500, 0.13),
    ]
    _NOMOGRAM_RI_1000 = [
        (1, 0.99), (5, 0.95), (10, 0.91), (20, 0.84),
        (50, 0.70), (100, 0.55), (200, 0.40), (500, 0.22),
    ]

    def __init__(
        self,
        Q: float,
        rho_release: float,
        T_release: float = 293.15,
        u: float = 5.0,
        H: float = 0.0,
        pool_area: Optional[float] = None,
        MW: float = 100.0,
        total_mass: Optional[float] = None,
    ):
        """Initialize Heavy Gas model.

        Args:
            Q: Release rate in kg/s (continuous) or 0 for instantaneous
            rho_release: Release gas density in kg/m³
            T_release: Release temperature in K
            u: Wind speed in m/s
            H: Release height in m
            pool_area: Pool area in m² (for initial cloud diameter)
            MW: Molecular weight in g/mol
            total_mass: Total mass in kg (for instantaneous release)
        """
        if u <= 0:
            raise ValueError("Wind speed must be greater than 0")
        if rho_release <= 0:
            raise ValueError("Release density must be positive")

        self.Q = Q
        self.rho_release = rho_release
        self.T_release = T_release
        self.u = u
        self.H = H
        self.MW = MW
        self.total_mass = total_mass or Q * 3600  # default 1-hour release

        # Calculate initial cloud properties
        if pool_area:
            self.D = 2.0 * np.sqrt(pool_area / np.pi)  # equivalent diameter
        else:
            # Estimate from release rate
            V_rate = Q / rho_release  # volumetric flow rate m³/s
            self.D = (4.0 * V_rate / np.pi) ** 0.5 * 10  # rough estimate

        self.V0 = self.total_mass / rho_release  # initial volume m³

    def is_heavy_gas(self) -> bool:
        """Check if gas is heavier than air (density ratio > 1.05)."""
        return self.rho_release / self.RHO_AIR > 1.05

    def get_richardson_number(self) -> float:
        """Calculate Richardson number.

        Ri = g · (ρr - ρa) · Vr / (ρa · u² · D²)
        """
        delta_rho = self.rho_release - self.RHO_AIR
        Ri = self.G * delta_rho * self.V0 / (self.RHO_AIR * self.u ** 2 * self.D ** 2)
        return max(Ri, 0.0)

    def _get_concentration_ratio(self, x_over_D: float, Ri: float) -> float:
        """Interpolate concentration ratio C/C0 from nomogram.

        Uses log-log interpolation between nomogram curves.
        """
        if x_over_D <= 0:
            return 1.0

        # Select nomogram data based on Richardson number
        if Ri <= 10:
            nomo = self._NOMOGRAM_RI_10
        elif Ri >= 1000:
            nomo = self._NOMOGRAM_RI_1000
        elif Ri <= 100:
            # Interpolate between Ri=10 and Ri=100
            frac = (np.log10(Ri) - 1) / 1.0  # 0 at Ri=10, 1 at Ri=100
            c_low = self._interpolate_nomogram(self._NOMOGRAM_RI_10, x_over_D)
            c_high = self._interpolate_nomogram(self._NOMOGRAM_RI_100, x_over_D)
            return c_low * (1 - frac) + c_high * frac
        else:
            # Interpolate between Ri=100 and Ri=1000
            frac = (np.log10(Ri) - 2) / 1.0
            c_low = self._interpolate_nomogram(self._NOMOGRAM_RI_100, x_over_D)
            c_high = self._interpolate_nomogram(self._NOMOGRAM_RI_1000, x_over_D)
            return c_low * (1 - frac) + c_high * frac

        return self._interpolate_nomogram(nomo, x_over_D)

    def _interpolate_nomogram(self, data: list, x_over_D: float) -> float:
        """Log-log interpolation from nomogram data points."""
        if x_over_D <= data[0][0]:
            return data[0][1]
        if x_over_D >= data[-1][0]:
            return data[-1][1] * (data[-2][1] / data[-1][1]) ** (
                np.log(x_over_D / data[-1][0]) / np.log(data[-1][0] / data[-2][0])
            )

        for i in range(len(data) - 1):
            x1, c1 = data[i]
            x2, c2 = data[i + 1]
            if x1 <= x_over_D <= x2:
                # Log-log interpolation
                if x1 == x2:
                    return c1
                log_frac = np.log(x_over_D / x1) / np.log(x2 / x1)
                return c1 * (c2 / c1) ** log_frac

        return data[-1][1]

    def get_central_concentration(self, x: float) -> float:
        """Get centerline concentration at distance x in ppm.

        Args:
            x: Downwind distance in meters

        Returns:
            Concentration in ppm (volume fraction)
        """
        if x <= 0:
            return 0.0

        Ri = self.get_richardson_number()
        x_over_D = x / max(self.D, 0.1)
        C_ratio = self._get_concentration_ratio(x_over_D, Ri)

        # C0 = initial volume fraction (pure gas = 1.0)
        C0 = 1.0

        # Convert to ppm: C_ratio * C0 is volume fraction
        return C_ratio * C0 * 1e6

    def get_cloud_half_width(self, x: float) -> float:
        """Get cloud half-width at distance x.

        Args:
            x: Downwind distance in meters

        Returns:
            Half-width in meters
        """
        if x <= 0:
            return self.D / 2.0

        # Cloud spreads approximately as x^0.5 for dense gas
        Ri = self.get_richardson_number()
        # Empirical: b ≈ D/2 * (1 + α * sqrt(x/D)) where α depends on Ri
        alpha = 0.5 * min(Ri ** 0.25, 5.0)
        x_over_D = x / max(self.D, 0.1)
        return self.D / 2.0 * (1.0 + alpha * np.sqrt(x_over_D))

    def get_transition_distance(self) -> float:
        """Find distance where dense gas transitions to passive (Gaussian).

        Transition when C/C0 ≈ 0.001 or Richardson number effect diminishes.
        """
        Ri = self.get_richardson_number()
        # Approximate: transition at x/D where C/C0 ≈ 0.01
        # From nomograms, roughly x/D ≈ Ri^0.5 * 100
        x_trans_D = min(Ri ** 0.5 * 100, 10000)
        return x_trans_D * self.D

    def get_threshold_distances(self, threshold_ppm: float) -> Dict[str, float]:
        """Find distances where concentration equals threshold.

        Returns:
            Dict with 'far' distance in meters
        """
        x_values = np.linspace(1, 50000, 5000)
        concentrations = np.array([self.get_central_concentration(x) for x in x_values])

        above = concentrations >= threshold_ppm
        far = 0.0

        for i in range(len(above)):
            if above[i]:
                far = x_values[i]

        return {"far": far}

    def calculate_concentration_grid(
        self,
        x_range: Tuple[float, float] = (10, 5000),
        y_range: Tuple[float, float] = (-1000, 1000),
        z: float = 0.0,
        resolution: int = 200,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculate concentration grid.

        Uses top-hat profile converted to equivalent Gaussian.
        """
        x = np.linspace(x_range[0], max(x_range[1], x_range[0] + 1), resolution)
        y = np.linspace(y_range[0], y_range[1], resolution)
        X, Y = np.meshgrid(x, y)

        C_grid = np.zeros_like(X)

        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                xi = X[i, j]
                yi = abs(Y[i, j])

                if xi <= 0:
                    continue

                c_center = self.get_central_concentration(xi)
                half_w = self.get_cloud_half_width(xi)

                # Top-hat to Gaussian conversion
                if half_w > 0:
                    sigma = half_w / np.sqrt(2)  # equivalent Gaussian sigma
                    C_grid[i, j] = c_center * np.exp(-0.5 * (yi / sigma) ** 2)

        return X, Y, C_grid
