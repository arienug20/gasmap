"""Chemical model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Float, Boolean, Text, TIMESTAMP, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Chemical(Base):
    """Chemical model."""

    __tablename__ = "chemicals"

    # Primary identifier
    cas_number = Column(String(20), primary_key=True)

    # Basic info
    name = Column(String(255), nullable=False, index=True)
    synonyms = Column(Text)  # JSON array
    formula = Column(String(100))
    smiles = Column(String(500))

    # Physical properties
    molecular_weight = Column(Float, nullable=False)
    boiling_point = Column(Float)  # °C
    melting_point = Column(Float)  # °C
    density_liquid = Column(Float)  # kg/m³
    density_gas = Column(Float)  # kg/m³ @ STP
    vapor_pressure = Column(Float)  # Pa @ 25°C
    is_heavier_than_air = Column(Boolean, default=False)

    # Gas category (comma-separated)
    gas_category = Column(String(100))  # flammable,toxic,asphyxiant,corrosive

    # Emergency thresholds
    erpg_1 = Column(Float)  # ppm
    erpg_2 = Column(Float)
    erpg_3 = Column(Float)
    idlh = Column(Float)  # ppm

    # AEGL values (ppm)
    aegl_1_10min = Column(Float)
    aegl_1_30min = Column(Float)
    aegl_1_60min = Column(Float)
    aegl_1_4hr = Column(Float)
    aegl_2_10min = Column(Float)
    aegl_2_30min = Column(Float)
    aegl_2_60min = Column(Float)
    aegl_2_4hr = Column(Float)
    aegl_3_10min = Column(Float)
    aegl_3_30min = Column(Float)
    aegl_3_60min = Column(Float)
    aegl_3_4hr = Column(Float)

    # Occupational limits
    lc50 = Column(Float)  # ppm
    pel = Column(Float)  # ppm
    rel = Column(Float)  # ppm
    tlv_twa = Column(Float)  # ppm
    tlv_stel = Column(Float)  # ppm

    # Flammability
    lel = Column(Float)  # % vol
    uel = Column(Float)  # % vol
    auto_ignition_temp = Column(Float)  # °C

    # Metadata
    source = Column(String(255))
    last_updated = Column(TIMESTAMP, default=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("idx_chemicals_category", "gas_category"),
    )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "cas_number": self.cas_number,
            "name": self.name,
            "synonyms": self.synonyms,
            "formula": self.formula,
            "smiles": self.smiles,
            "molecular_weight": self.molecular_weight,
            "boiling_point": self.boiling_point,
            "melting_point": self.melting_point,
            "density_liquid": self.density_liquid,
            "density_gas": self.density_gas,
            "vapor_pressure": self.vapor_pressure,
            "is_heavier_than_air": self.is_heavier_than_air,
            "gas_category": self.gas_category,
            "erpg_1": self.erpg_1,
            "erpg_2": self.erpg_2,
            "erpg_3": self.erpg_3,
            "idlh": self.idlh,
            "aegl_1_10min": self.aegl_1_10min,
            "aegl_1_30min": self.aegl_1_30min,
            "aegl_1_60min": self.aegl_1_60min,
            "aegl_1_4hr": self.aegl_1_4hr,
            "aegl_2_10min": self.aegl_2_10min,
            "aegl_2_30min": self.aegl_2_30min,
            "aegl_2_60min": self.aegl_2_60min,
            "aegl_2_4hr": self.aegl_2_4hr,
            "aegl_3_10min": self.aegl_3_10min,
            "aegl_3_30min": self.aegl_3_30min,
            "aegl_3_60min": self.aegl_3_60min,
            "aegl_3_4hr": self.aegl_3_4hr,
            "lc50": self.lc50,
            "pel": self.pel,
            "rel": self.rel,
            "tlv_twa": self.tlv_twa,
            "tlv_stel": self.tlv_stel,
            "lel": self.lel,
            "uel": self.uel,
            "auto_ignition_temp": self.auto_ignition_temp,
            "source": self.source,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }