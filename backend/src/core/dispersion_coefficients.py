"""Pasquill-Gifford dispersion coefficients (Briggs formulations)."""

import numpy as np
from typing import Tuple


# Briggs urban coefficients for σy: σy = a * x / (1 + b * x)^0.5
# x in meters, σy in meters
_BRIGGS_RURAL_SY = {
    "A": (0.22, 0.0001),
    "B": (0.16, 0.0001),
    "C": (0.11, 0.0001),
    "D": (0.08, 0.0001),
    "E": (0.06, 0.0001),
    "F": (0.04, 0.0001),
}

# Briggs rural σz: σz = a * x
_BRIGGS_RURAL_SZ = {
    "A": (0.20,),
    "B": (0.12,),
    "C": (0.08,),
    "D": (0.06,),
    "E": (0.03,),
    "F": (0.016,),
}

# Briggs urban coefficients
_BRIGGS_URBAN_SY = {
    "A": (0.32, 0.0004),
    "B": (0.32, 0.0004),
    "C": (0.22, 0.0004),
    "D": (0.16, 0.0004),
    "E": (0.11, 0.0004),
    "F": (0.11, 0.0004),
}

_BRIGGS_URBAN_SZ = {
    "A": (0.24,),
    "B": (0.24,),
    "C": (0.20,),
    "D": (0.14,),
    "E": (0.08,),
    "F": (0.06,),
}

# Pasquill-Gifford σy coefficients: σy = (a * x^b) where x in km
# Using standard PG tables (Turner, 1969)
_PG_SY_COEFFICIENTS = {
    "A": (0.3658, 0.9031),
    "B": (0.2751, 0.9031),
    "C": (0.2090, 0.9031),
    "D": (0.1471, 0.9031),
    "E": (0.1046, 0.9031),
    "F": (0.0722, 0.9031),
}

# Pasquill-Gifford σz coefficients: σz = (a * x^b) where x in km
_PG_SZ_COEFFICIENTS = {
    "A": (0.192, 1.0857),   # σz capped at 5000m
    "B": (0.156, 0.9823),   # σz capped at 5000m
    "C": (0.116, 0.9823),
    "D": (0.079, 0.8060),
    "E": (0.063, 0.8060),
    "F": (0.053, 0.8060),
}


def get_sigma_y(x: float, stability: str, terrain: str = "rural") -> float:
    """Calculate lateral dispersion coefficient σy.

    Args:
        x: Downwind distance in meters (must be > 0)
        stability: Pasquill stability class A-F
        terrain: 'rural' or 'urban'

    Returns:
        σy in meters
    """
    if x <= 0:
        return 0.0

    stability = stability.upper()
    if stability not in "ABCDEF":
        raise ValueError(f"Invalid stability class: {stability}")

    # Use Briggs formulations
    if terrain == "urban":
        a, b = _BRIGGS_URBAN_SY[stability]
    else:
        a, b = _BRIGGS_RURAL_SY[stability]

    sigma_y = a * x / (1.0 + b * x) ** 0.5
    return max(sigma_y, 1e-10)


def get_sigma_z(x: float, stability: str, terrain: str = "rural") -> float:
    """Calculate vertical dispersion coefficient σz.

    Args:
        x: Downwind distance in meters (must be > 0)
        stability: Pasquill stability class A-F
        terrain: 'rural' or 'urban'

    Returns:
        σz in meters
    """
    if x <= 0:
        return 0.0

    stability = stability.upper()
    if stability not in "ABCDEF":
        raise ValueError(f"Invalid stability class: {stability}")

    if terrain == "urban":
        coeffs = _BRIGGS_URBAN_SZ[stability]
    else:
        coeffs = _BRIGGS_RURAL_SZ[stability]

    sigma_z = coeffs[0] * x

    # Cap σz at mixing height for stable conditions
    if stability in ("E", "F"):
        sigma_z = min(sigma_z, 5000.0)

    return max(sigma_z, 1e-10)


def get_sigma_y_vectorized(x_arr: np.ndarray, stability: str, terrain: str = "rural") -> np.ndarray:
    """Vectorized σy calculation."""
    stability = stability.upper()
    if terrain == "urban":
        a, b = _BRIGGS_URBAN_SY[stability]
    else:
        a, b = _BRIGGS_RURAL_SY[stability]

    x = np.maximum(x_arr, 0.0)
    sigma = np.where(x > 0, a * x / np.sqrt(1.0 + b * x), 0.0)
    return np.maximum(sigma, 1e-10)


def get_sigma_z_vectorized(x_arr: np.ndarray, stability: str, terrain: str = "rural") -> np.ndarray:
    """Vectorized σz calculation."""
    stability = stability.upper()
    if terrain == "urban":
        coeffs = _BRIGGS_URBAN_SZ[stability]
    else:
        coeffs = _BRIGGS_RURAL_SZ[stability]

    x = np.maximum(x_arr, 0.0)
    sigma = np.where(x > 0, coeffs[0] * x, 0.0)

    if stability in ("E", "F"):
        sigma = np.minimum(sigma, 5000.0)

    return np.maximum(sigma, 1e-10)
