"""Chemical database service."""

import json
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.models.chemical import Chemical


class ChemicalService:
    """Service for chemical database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_count(self) -> int:
        """Get total chemical count."""
        return self.db.query(Chemical).count()

    def get_all(self, page: int = 1, per_page: int = 50, category: Optional[str] = None) -> List[Chemical]:
        """Get all chemicals with pagination."""
        query = self.db.query(Chemical)
        if category:
            query = query.filter(Chemical.gas_category.contains(category))
        offset = (page - 1) * per_page
        return query.offset(offset).limit(per_page).all()

    def get_by_cas(self, cas_number: str) -> Optional[Chemical]:
        """Get chemical by CAS number."""
        return self.db.query(Chemical).filter(Chemical.cas_number == cas_number).first()

    def search(self, query: str) -> List[Chemical]:
        """Search chemicals by name, synonym, formula, or CAS."""
        search_term = f"%{query}%"
        return self.db.query(Chemical).filter(
            or_(
                Chemical.name.ilike(search_term),
                Chemical.synonyms.ilike(search_term),
                Chemical.formula.ilike(search_term),
                Chemical.cas_number.ilike(search_term),
            )
        ).all()

    def get_categories(self) -> List[dict]:
        """Get all categories with counts."""
        chemicals = self.db.query(Chemical).all()
        cats = {}
        for chem in chemicals:
            if chem.gas_category:
                for cat in chem.gas_category.split(","):
                    cat = cat.strip()
                    cats[cat] = cats.get(cat, 0) + 1
        return [{"category": k, "count": v} for k, v in sorted(cats.items())]

    def get_thresholds(self, cas_number: str) -> Optional[dict]:
        """Get all thresholds for a chemical."""
        chem = self.get_by_cas(cas_number)
        if not chem:
            return None
        return {
            "cas_number": chem.cas_number,
            "name": chem.name,
            "erpg_1": chem.erpg_1,
            "erpg_2": chem.erpg_2,
            "erpg_3": chem.erpg_3,
            "idlh": chem.idlh,
            "aegl_1_10min": chem.aegl_1_10min,
            "aegl_1_30min": chem.aegl_1_30min,
            "aegl_1_60min": chem.aegl_1_60min,
            "aegl_1_4hr": chem.aegl_1_4hr,
            "aegl_2_10min": chem.aegl_2_10min,
            "aegl_2_30min": chem.aegl_2_30min,
            "aegl_2_60min": chem.aegl_2_60min,
            "aegl_2_4hr": chem.aegl_2_4hr,
            "aegl_3_10min": chem.aegl_3_10min,
            "aegl_3_30min": chem.aegl_3_30min,
            "aegl_3_60min": chem.aegl_3_60min,
            "aegl_3_4hr": chem.aegl_3_4hr,
        }

    def seed_from_json(self, filepath: str) -> int:
        """Seed database from JSON file."""
        with open(filepath, "r") as f:
            chemicals = json.load(f)

        count = 0
        for data in chemicals:
            existing = self.get_by_cas(data["cas_number"])
            if existing:
                continue

            chem = Chemical(
                cas_number=data["cas_number"],
                name=data["name"],
                synonyms=json.dumps(data.get("synonyms", [])),
                formula=data.get("formula"),
                molecular_weight=data["molecular_weight"],
                boiling_point=data.get("boiling_point"),
                melting_point=data.get("melting_point"),
                density_liquid=data.get("density_liquid"),
                density_gas=data.get("density_gas"),
                vapor_pressure=data.get("vapor_pressure"),
                is_heavier_than_air=data.get("is_heavier_than_air", False),
                gas_category=data.get("gas_category"),
                erpg_1=data.get("erpg_1"),
                erpg_2=data.get("erpg_2"),
                erpg_3=data.get("erpg_3"),
                idlh=data.get("idlh"),
                aegl_1_10min=data.get("aegl_1_10min"),
                aegl_1_30min=data.get("aegl_1_30min"),
                aegl_1_60min=data.get("aegl_1_60min"),
                aegl_1_4hr=data.get("aegl_1_4hr"),
                aegl_2_10min=data.get("aegl_2_10min"),
                aegl_2_30min=data.get("aegl_2_30min"),
                aegl_2_60min=data.get("aegl_2_60min"),
                aegl_2_4hr=data.get("aegl_2_4hr"),
                aegl_3_10min=data.get("aegl_3_10min"),
                aegl_3_30min=data.get("aegl_3_30min"),
                aegl_3_60min=data.get("aegl_3_60min"),
                aegl_3_4hr=data.get("aegl_3_4hr"),
                lc50=data.get("lc50"),
                pel=data.get("pel"),
                rel=data.get("rel"),
                tlv_twa=data.get("tlv_twa"),
                tlv_stel=data.get("tlv_stel"),
                lel=data.get("lel"),
                uel=data.get("uel"),
                auto_ignition_temp=data.get("auto_ignition_temp"),
                source=data.get("source"),
            )
            self.db.add(chem)
            count += 1

        self.db.commit()
        return count
