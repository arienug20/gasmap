"""Scenarios CRUD + export/import router."""

import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.scenario import Scenario

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


class ScenarioCreate(BaseModel):
    name: str
    description: str = ""
    chemical_cas: str
    chemical_name: str
    model: str = "gaussian_plume"
    emission_rate: Optional[float] = None
    total_mass: Optional[float] = None
    release_height: float = 0.0
    release_density: Optional[float] = None
    wind_speed: float = 5.0
    stability_class: str = "D"
    terrain: str = "rural"
    ambient_temp: float = 25.0
    grid_resolution: int = 100
    grid_size_x: float = 5000.0
    grid_size_y: float = 2000.0
    results: Optional[dict] = None


class ScenarioUpdate(ScenarioCreate):
    name: Optional[str] = None
    description: Optional[str] = None
    chemical_cas: Optional[str] = None
    chemical_name: Optional[str] = None


@router.post("", status_code=201)
def create_scenario(data: ScenarioCreate, db: Session = Depends(get_db)):
    """Create a new scenario."""
    sc = Scenario(
        name=data.name,
        description=data.description,
        chemical_cas=data.chemical_cas,
        chemical_name=data.chemical_name,
        model=data.model,
        emission_rate=data.emission_rate,
        total_mass=data.total_mass,
        release_height=data.release_height,
        release_density=data.release_density,
        wind_speed=data.wind_speed,
        stability_class=data.stability_class,
        terrain=data.terrain,
        ambient_temp=data.ambient_temp,
        grid_resolution=data.grid_resolution,
        grid_size_x=data.grid_size_x,
        grid_size_y=data.grid_size_y,
        results_json=json.dumps(data.results) if data.results else None,
    )
    db.add(sc)
    db.commit()
    db.refresh(sc)
    return sc.to_dict()


@router.get("")
def list_scenarios(db: Session = Depends(get_db)):
    """List all saved scenarios."""
    scenarios = db.query(Scenario).order_by(Scenario.updated_at.desc()).all()
    return {"scenarios": [s.to_dict() for s in scenarios]}


@router.get("/{scenario_id}")
def get_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """Get a specific scenario by ID."""
    sc = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not sc:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return sc.to_dict()


@router.put("/{scenario_id}")
def update_scenario(scenario_id: int, data: ScenarioUpdate, db: Session = Depends(get_db)):
    """Update an existing scenario."""
    sc = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not sc:
        raise HTTPException(status_code=404, detail="Scenario not found")
    update_data = data.dict(exclude_unset=True, exclude={"results"})
    results = data.results
    for key, value in update_data.items():
        setattr(sc, key, value)
    if results is not None:
        sc.results_json = json.dumps(results)
    db.commit()
    db.refresh(sc)
    return sc.to_dict()


@router.delete("/{scenario_id}")
def delete_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """Delete a scenario."""
    sc = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not sc:
        raise HTTPException(status_code=404, detail="Scenario not found")
    db.delete(sc)
    db.commit()
    return {"status": "deleted", "id": scenario_id}


@router.get("/{scenario_id}/export")
def export_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """Export scenario as downloadable JSON."""
    sc = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not sc:
        raise HTTPException(status_code=404, detail="Scenario not found")
    data = sc.to_dict()
    return JSONResponse(content=data, headers={
        "Content-Disposition": f'attachment; filename="scenario_{scenario_id}.json"'
    })


@router.post("/import", status_code=201)
def import_scenario(data: dict, db: Session = Depends(get_db)):
    """Import a scenario from JSON."""
    required = ["name", "chemical_cas", "chemical_name"]
    for field in required:
        if field not in data:
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")
    sc = Scenario(
        name=data.get("name", "Imported Scenario"),
        description=data.get("description", ""),
        chemical_cas=data["chemical_cas"],
        chemical_name=data["chemical_name"],
        model=data.get("model", "gaussian_plume"),
        emission_rate=data.get("emission_rate"),
        total_mass=data.get("total_mass"),
        release_height=data.get("release_height", 0.0),
        release_density=data.get("release_density"),
        wind_speed=data.get("wind_speed", 5.0),
        stability_class=data.get("stability_class", "D"),
        terrain=data.get("terrain", "rural"),
        ambient_temp=data.get("ambient_temp", 25.0),
        grid_resolution=data.get("grid_resolution", 100),
        grid_size_x=data.get("grid_size_x", 5000.0),
        grid_size_y=data.get("grid_size_y", 2000.0),
        results_json=json.dumps(data["results"]) if "results" in data and data["results"] else None,
    )
    db.add(sc)
    db.commit()
    db.refresh(sc)
    return sc.to_dict()
