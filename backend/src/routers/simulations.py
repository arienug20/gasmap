"""Simulations API router."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import time

from src.database import get_db
from src.services.chemical_service import ChemicalService
from src.core.gaussian_plume import GaussianPlume
from src.core.gaussian_puff import GaussianPuff
from src.core.heavy_gas_bm import HeavyGasBM

router = APIRouter(prefix="/simulations", tags=["simulations"])


class SimulationRequest(BaseModel):
    """Simulation run request."""
    chemical_cas: str
    model: str  # gaussian_plume, gaussian_puff, heavy_gas
    # Release params
    emission_rate: Optional[float] = None  # kg/s
    total_mass: Optional[float] = None  # kg (puff)
    release_height: float = 0.0  # m
    # Weather
    wind_speed: float = 5.0  # m/s
    stability_class: str = "D"
    terrain: str = "rural"
    ambient_temp: float = 25.0
    # Grid
    grid_resolution: int = 100
    grid_size_x: float = 5000.0
    grid_size_y: float = 2000.0
    # Heavy gas
    release_density: Optional[float] = None  # kg/m³


@router.post("/run")
def run_simulation(request: SimulationRequest, db=Depends(get_db)):
    """Run a dispersion simulation."""
    start = time.time()

    # Get chemical
    service = ChemicalService(db)
    chem = service.get_by_cas(request.chemical_cas)
    if not chem:
        raise HTTPException(status_code=404, detail="Chemical not found")

    MW = chem.molecular_weight

    x_range = (10, request.grid_size_x)
    y_range = (-request.grid_size_y / 2, request.grid_size_y / 2)

    try:
        if request.model == "gaussian_plume":
            Q = request.emission_rate or 1.0
            model = GaussianPlume(
                Q=Q, u=request.wind_speed, H=request.release_height,
                stability=request.stability_class, terrain=request.terrain, MW=MW,
            )
            X, Y, C = model.calculate_concentration_grid(
                x_range=x_range, y_range=y_range,
                resolution=request.grid_resolution,
            )
        elif request.model == "gaussian_puff":
            Q_total = request.total_mass or 1000.0
            model = GaussianPuff(
                Q_total=Q_total, u=request.wind_speed, H=request.release_height,
                stability=request.stability_class, terrain=request.terrain, MW=MW,
            )
            C = model.get_max_concentration_envelope(
                x_range=x_range, y_range=y_range,
                resolution=request.grid_resolution,
            )
        elif request.model == "heavy_gas":
            Q = request.emission_rate or 1.0
            rho = request.release_density or chem.density_gas or (MW / 22.414 * 101325 / 101325)
            model = HeavyGasBM(
                Q=Q, rho_release=rho, u=request.wind_speed,
                H=request.release_height, MW=MW,
            )
            X, Y, C = model.calculate_concentration_grid(
                x_range=x_range, y_range=y_range,
                resolution=request.grid_resolution,
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown model: {request.model}")

        # Extract summary metrics
        max_c = float(C.max())

        # Threshold distances
        thresholds = {}
        if chem.erpg_1:
            thresholds["erpg_1"] = chem.erpg_1
        if chem.erpg_2:
            thresholds["erpg_2"] = chem.erpg_2
        if chem.erpg_3:
            thresholds["erpg_3"] = chem.erpg_3
        if chem.idlh:
            thresholds["idlh"] = chem.idlh

        elapsed = (time.time() - start) * 1000

        return {
            "status": "success",
            "model": request.model,
            "chemical": {"cas": chem.cas_number, "name": chem.name, "MW": MW},
            "max_concentration_ppm": max_c,
            "thresholds": thresholds,
            "grid_resolution": request.grid_resolution,
            "grid_shape": list(C.shape),
            "computation_time_ms": round(elapsed, 1),
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
