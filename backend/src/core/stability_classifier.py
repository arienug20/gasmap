"""Pasquill stability class classifier."""

from typing import Optional


def classify_stability(
    wind_speed: float,
    is_daytime: bool = True,
    solar_radiation: Optional[str] = None,
    cloud_cover: Optional[float] = None,
    wind_direction_sigma: Optional[float] = None,
) -> str:
    """Classify Pasquill stability class from weather parameters.

    Args:
        wind_speed: Wind speed in m/s
        is_daytime: True for daytime, False for nighttime
        solar_radiation: 'strong', 'moderate', or 'slight' (daytime only)
        cloud_cover: Cloud cover in tenths (0-10, nighttime)
        wind_direction_sigma: Standard deviation of wind direction in degrees (optional)

    Returns:
        Stability class A-F

    Raises:
        ValueError: If wind_speed <= 0 or invalid parameters
    """
    if wind_speed < 0:
        raise ValueError("Wind speed must be non-negative")
    if wind_speed == 0:
        wind_speed = 0.5  # Minimum effective wind speed

    # σθ method if wind direction data available
    if wind_direction_sigma is not None:
        if wind_direction_sigma < 10:
            return "F"
        elif wind_direction_sigma < 15:
            return "E"
        elif wind_direction_sigma < 20:
            return "D"
        elif wind_direction_sigma < 30:
            return "C"
        elif wind_direction_sigma < 45:
            return "B"
        else:
            return "A"

    if is_daytime:
        if solar_radiation is None:
            solar_radiation = "moderate"

        sr = solar_radiation.lower()
        if sr not in ("strong", "moderate", "slight"):
            raise ValueError(f"Invalid solar radiation: {sr}")

        if wind_speed < 2:
            table = {"strong": "A", "moderate": "A", "slight": "B"}
            return table[sr]
        elif wind_speed < 3:
            table = {"strong": "A", "moderate": "B", "slight": "C"}
            return table[sr]
        elif wind_speed < 5:
            table = {"strong": "B", "moderate": "C", "slight": "C"}
            return table[sr]
        elif wind_speed < 6:
            table = {"strong": "C", "moderate": "C", "slight": "D"}
            return table[sr]
        else:
            table = {"strong": "C", "moderate": "D", "slight": "D"}
            return table[sr]
    else:
        # Nighttime
        if cloud_cover is None:
            cloud_cover = 5.0

        if wind_speed < 2:
            if cloud_cover <= 3.75:  # ≤3/8
                return "F"
            elif cloud_cover <= 7.5:
                return "E"
            else:
                return "D"
        elif wind_speed < 3:
            if cloud_cover <= 3.75:
                return "E"
            else:
                return "D"
        elif wind_speed < 5:
            return "D"
        else:
            return "D"
