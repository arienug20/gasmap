"""Unit converter for gas dispersion calculations."""

import math


def ppm_to_mgm3(ppm: float, MW: float, T: float = 25.0, P: float = 101325.0) -> float:
    """Convert ppm to mg/m³.

    Args:
        ppm: Concentration in ppm
        MW: Molecular weight in g/mol
        T: Temperature in °C
        P: Pressure in Pa

    Returns:
        Concentration in mg/m³
    """
    return ppm * MW / (22.414 * (T + 273.15) / 273.15 * 101325.0 / P)


def mgm3_to_ppm(mgm3: float, MW: float, T: float = 25.0, P: float = 101325.0) -> float:
    """Convert mg/m³ to ppm.

    Args:
        mgm3: Concentration in mg/m³
        MW: Molecular weight in g/mol
        T: Temperature in °C
        P: Pressure in Pa

    Returns:
        Concentration in ppm
    """
    return mgm3 * 22.414 * (T + 273.15) / 273.15 * 101325.0 / P / MW


def kg_s_to_g_s(kg_s: float) -> float:
    """Convert kg/s to g/s."""
    return kg_s * 1000.0


def concentration_to_ppm(C_kgm3: float, MW: float, T: float = 25.0, P: float = 101325.0) -> float:
    """Convert model output concentration (kg/m³) to ppm.

    Args:
        C_kgm3: Concentration in kg/m³
        MW: Molecular weight in g/mol
        T: Temperature in °C
        P: Pressure in Pa

    Returns:
        Concentration in ppm (volume)
    """
    # kg/m³ → mg/m³ → ppm
    mgm3 = C_kgm3 * 1e6  # kg/m³ to mg/m³
    return mgm3_to_ppm(mgm3, MW, T, P)


def ppm_to_kgm3(ppm: float, MW: float, T: float = 25.0, P: float = 101325.0) -> float:
    """Convert ppm to kg/m³.

    Args:
        ppm: Concentration in ppm (volume)
        MW: Molecular weight in g/mol
        T: Temperature in °C
        P: Pressure in Pa

    Returns:
        Concentration in kg/m³
    """
    mgm3 = ppm_to_mgm3(ppm, MW, T, P)
    return mgm3 * 1e-6  # mg/m³ to kg/m³
