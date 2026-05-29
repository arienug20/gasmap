"""Test configuration and fixtures."""

import pytest
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.models.chemical import Base, Chemical


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_chemical(db_session):
    """Add a sample chemical to the test database."""
    chem = Chemical(
        cas_number="7782-50-5",
        name="Chlorine",
        synonyms='["Bertholite"]',
        formula="Cl2",
        molecular_weight=70.9,
        boiling_point=-34.04,
        density_gas=3.21,
        is_heavier_than_air=True,
        gas_category="toxic,corrosive",
        erpg_1=1.0,
        erpg_2=3.0,
        erpg_3=20.0,
        idlh=10.0,
        aegl_1_10min=0.5,
        aegl_2_10min=2.8,
        aegl_3_10min=50.0,
        pel=0.5,
        tlv_twa=0.5,
    )
    db_session.add(chem)
    db_session.commit()
    return chem
