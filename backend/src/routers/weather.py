"""Weather API router."""

from fastapi import APIRouter, Query
from src.core.stability_classifier import classify_stability

router = APIRouter(prefix="/weather", tags=["weather"])

PRESETS = [
    {
        "name": "Worst Case Day",
        "wind_speed": 1.5,
        "stability_class": "A",
        "temperature": 35.0,
        "humidity": 30.0,
        "is_daytime": True,
    },
    {
        "name": "Worst Case Night",
        "wind_speed": 1.5,
        "stability_class": "F",
        "temperature": 15.0,
        "humidity": 80.0,
        "is_daytime": False,
    },
    {
        "name": "Typical Day",
        "wind_speed": 5.0,
        "stability_class": "C",
        "temperature": 28.0,
        "humidity": 60.0,
        "is_daytime": True,
    },
    {
        "name": "Typical Night",
        "wind_speed": 3.0,
        "stability_class": "E",
        "temperature": 22.0,
        "humidity": 70.0,
        "is_daytime": False,
    },
    {
        "name": "High Wind",
        "wind_speed": 10.0,
        "stability_class": "D",
        "temperature": 25.0,
        "humidity": 50.0,
        "is_daytime": True,
    },
    {
        "name": "Tropical Hot",
        "wind_speed": 2.0,
        "stability_class": "B",
        "temperature": 38.0,
        "humidity": 40.0,
        "is_daytime": True,
    },
]


@router.get("/presets")
def get_weather_presets():
    """List preset weather scenarios."""
    return {"presets": PRESETS}


@router.get("/stability-class")
def calculate_stability_class(
    wind_speed: float = Query(..., gt=0),
    is_daytime: bool = True,
    solar_radiation: str = "moderate",
    cloud_cover: float = 5.0,
):
    """Calculate Pasquill stability class from weather parameters."""
    try:
        stability = classify_stability(
            wind_speed=wind_speed,
            is_daytime=is_daytime,
            solar_radiation=solar_radiation if is_daytime else None,
            cloud_cover=cloud_cover if not is_daytime else None,
        )
        return {"stability_class": stability}
    except ValueError as e:
        return {"error": str(e)}
