"""Grid computation engine (NumPy vectorized)."""

import numpy as np
import zlib
from typing import Tuple, Optional


class GridEngine:
    """Vectorized concentration grid computation."""

    def __init__(
        self,
        x_range: Tuple[float, float] = (10, 5000),
        y_range: Tuple[float, float] = (-1000, 1000),
        resolution: int = 200,
    ):
        self.resolution = resolution
        self.x = np.linspace(x_range[0], max(x_range[1], x_range[0] + 1), resolution)
        self.y = np.linspace(y_range[0], y_range[1], resolution)
        self.X, self.Y = np.meshgrid(self.x, self.y)

    def compute_gaussian_plume(
        self,
        Q: float,
        u: float,
        H: float,
        sigma_y_fn,
        sigma_z_fn,
        z: float = 0.0,
    ) -> np.ndarray:
        """Fully vectorized Gaussian plume computation.

        Args:
            Q: Emission rate (kg/s)
            u: Wind speed (m/s)
            H: Release height (m)
            sigma_y_fn: Function(x) -> σy
            sigma_z_fn: Function(x) -> σz
            z: Receptor height (m)

        Returns:
            Concentration grid in kg/m³
        """
        sigma_y = np.vectorize(sigma_y_fn)(self.X)
        sigma_z = np.vectorize(sigma_z_fn)(self.X)

        sigma_y = np.maximum(sigma_y, 1e-10)
        sigma_z = np.maximum(sigma_z, 1e-10)

        C = (Q / (2.0 * np.pi * u * sigma_y * sigma_z)) * \
            np.exp(-self.Y ** 2 / (2.0 * sigma_y ** 2)) * \
            (np.exp(-((z - H) ** 2) / (2.0 * sigma_z ** 2)) +
             np.exp(-((z + H) ** 2) / (2.0 * sigma_z ** 2)))

        return C

    @staticmethod
    def compress_grid(grid: np.ndarray) -> bytes:
        """Compress grid using zlib."""
        return zlib.compress(grid.astype(np.float32).tobytes())

    @staticmethod
    def decompress_grid(data: bytes, shape: Tuple[int, int]) -> np.ndarray:
        """Decompress grid from zlib."""
        return np.frombuffer(zlib.decompress(data), dtype=np.float32).reshape(shape)
