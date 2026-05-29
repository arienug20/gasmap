"""Tests for scenarios CRUD + export/import API."""

import pytest
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.models.chemical import Base
import src.models.scenario  # noqa
from src.database import get_db
from src.main import app


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


SAMPLE_SCENARIO = {
    "name": "Test Chlorine Release",
    "description": "Test scenario",
    "chemical_cas": "7782-50-5",
    "chemical_name": "Chlorine",
    "model": "gaussian_plume",
    "emission_rate": 10.0,
    "release_height": 0.0,
    "wind_speed": 5.0,
    "stability_class": "D",
    "terrain": "rural",
    "grid_resolution": 100,
    "grid_size_x": 5000.0,
    "grid_size_y": 2000.0,
}


def test_create_scenario(client):
    """Test POST /scenarios — create a new scenario."""
    r = client.post("/api/scenarios", json=SAMPLE_SCENARIO)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Test Chlorine Release"
    assert data["chemical_cas"] == "7782-50-5"
    assert data["id"] is not None


def test_list_scenarios(client):
    """Test GET /scenarios — list all scenarios."""
    client.post("/api/scenarios", json=SAMPLE_SCENARIO)
    r = client.get("/api/scenarios")
    assert r.status_code == 200
    assert len(r.json()["scenarios"]) >= 1


def test_get_scenario(client):
    """Test GET /scenarios/{id} — retrieve a specific scenario."""
    create = client.post("/api/scenarios", json=SAMPLE_SCENARIO).json()
    r = client.get(f"/api/scenarios/{create['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "Test Chlorine Release"


def test_update_scenario(client):
    """Test PUT /scenarios/{id} — update a scenario."""
    create = client.post("/api/scenarios", json=SAMPLE_SCENARIO).json()
    r = client.put(f"/api/scenarios/{create['id']}", json={
        **SAMPLE_SCENARIO,
        "name": "Updated Scenario",
        "wind_speed": 10.0,
    })
    assert r.status_code == 200
    assert r.json()["name"] == "Updated Scenario"
    assert r.json()["wind_speed"] == 10.0


def test_delete_scenario(client):
    """Test DELETE /scenarios/{id} — delete a scenario."""
    create = client.post("/api/scenarios", json=SAMPLE_SCENARIO).json()
    r = client.delete(f"/api/scenarios/{create['id']}")
    assert r.status_code == 200
    # Verify it's gone
    r2 = client.get(f"/api/scenarios/{create['id']}")
    assert r2.status_code == 404


def test_export_scenario(client):
    """Test GET /scenarios/{id}/export — export as JSON."""
    create = client.post("/api/scenarios", json=SAMPLE_SCENARIO).json()
    r = client.get(f"/api/scenarios/{create['id']}/export")
    assert r.status_code == 200
    assert "attachment" in r.headers.get("content-disposition", "")
    data = r.json()
    assert data["name"] == "Test Chlorine Release"


def test_import_scenario(client):
    """Test POST /scenarios/import — import from JSON."""
    export_data = {**SAMPLE_SCENARIO, "results": {"max_concentration_ppm": 500.0}}
    r = client.post("/api/scenarios/import", json=export_data)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Test Chlorine Release"
    assert data["results"]["max_concentration_ppm"] == 500.0


def test_import_missing_field(client):
    """Test POST /scenarios/import — reject missing required fields."""
    r = client.post("/api/scenarios/import", json={"name": "bad"})
    assert r.status_code == 400


def test_get_nonexistent_scenario(client):
    """Test GET /scenarios/{id} — 404 for missing scenario."""
    r = client.get("/api/scenarios/99999")
    assert r.status_code == 404
