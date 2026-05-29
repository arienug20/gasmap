"""Scenario model for saving/loading simulation configurations."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, TIMESTAMP
from src.models.chemical import Base


class Scenario(Base):
    """Saved scenario with all input parameters and optional results."""

    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, default="")

    # Chemical
    chemical_cas = Column(String(20), nullable=False)
    chemical_name = Column(String(255), nullable=False)

    # Model
    model = Column(String(50), nullable=False, default="gaussian_plume")

    # Release parameters
    emission_rate = Column(Float)
    total_mass = Column(Float)
    release_height = Column(Float, default=0.0)
    release_density = Column(Float)

    # Weather
    wind_speed = Column(Float, default=5.0)
    stability_class = Column(String(5), default="D")
    terrain = Column(String(20), default="rural")
    ambient_temp = Column(Float, default=25.0)

    # Grid
    grid_resolution = Column(Integer, default=100)
    grid_size_x = Column(Float, default=5000.0)
    grid_size_y = Column(Float, default=2000.0)

    # Results (JSON string)
    results_json = Column(Text)

    # Metadata
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        import json
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "chemical_cas": self.chemical_cas,
            "chemical_name": self.chemical_name,
            "model": self.model,
            "emission_rate": self.emission_rate,
            "total_mass": self.total_mass,
            "release_height": self.release_height,
            "release_density": self.release_density,
            "wind_speed": self.wind_speed,
            "stability_class": self.stability_class,
            "terrain": self.terrain,
            "ambient_temp": self.ambient_temp,
            "grid_resolution": self.grid_resolution,
            "grid_size_x": self.grid_size_x,
            "grid_size_y": self.grid_size_y,
            "results": json.loads(self.results_json) if self.results_json else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
