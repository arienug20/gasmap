"""Tests for Chemical Database."""

import pytest
import json
import os
from src.services.chemical_service import ChemicalService
from src.models.chemical import Chemical


class TestChemicalDatabase:
    """Chemical database tests."""

    def test_seed_chemicals_from_json(self, db_session):
        """Should seed chemicals from JSON file."""
        service = ChemicalService(db_session)
        data_path = os.path.join(os.path.dirname(__file__), "..", "src", "data", "seed_chemicals.json")
        count = service.seed_from_json(data_path)
        assert count >= 20, f"Should seed at least 20 chemicals, got {count}"

    def test_get_by_cas(self, db_session, sample_chemical):
        """Should retrieve chemical by CAS number."""
        service = ChemicalService(db_session)
        chem = service.get_by_cas("7782-50-5")
        assert chem is not None
        assert chem.name == "Chlorine"

    def test_search_by_name(self, db_session, sample_chemical):
        """Should search chemicals by name."""
        service = ChemicalService(db_session)
        results = service.search("chlorine")
        assert len(results) >= 1
        assert results[0].name == "Chlorine"

    def test_search_by_formula(self, db_session, sample_chemical):
        """Should search chemicals by formula."""
        service = ChemicalService(db_session)
        results = service.search("Cl2")
        assert len(results) >= 1

    def test_not_found_cas(self, db_session):
        """Should return None for non-existent CAS."""
        service = ChemicalService(db_session)
        chem = service.get_by_cas("0000-00-0")
        assert chem is None

    def test_get_categories(self, db_session, sample_chemical):
        """Should return categories with counts."""
        service = ChemicalService(db_session)
        cats = service.get_categories()
        assert len(cats) >= 1
        cat_names = [c["category"] for c in cats]
        assert "toxic" in cat_names

    def test_get_thresholds(self, db_session, sample_chemical):
        """Should return threshold data."""
        service = ChemicalService(db_session)
        thresholds = service.get_thresholds("7782-50-5")
        assert thresholds is not None
        assert thresholds["erpg_1"] == 1.0
        assert thresholds["erpg_2"] == 3.0
        assert thresholds["idlh"] == 10.0

    def test_heavier_than_air_flag(self, db_session, sample_chemical):
        """Chlorine should be flagged as heavier than air."""
        assert sample_chemical.is_heavier_than_air is True
        assert sample_chemical.molecular_weight > 28.97

    def test_seed_no_duplicates(self, db_session, sample_chemical):
        """Seeding should not duplicate existing chemicals."""
        service = ChemicalService(db_session)
        data_path = os.path.join(os.path.dirname(__file__), "..", "src", "data", "seed_chemicals.json")
        count = service.seed_from_json(data_path)
        # Chlorine already exists, should not be added again
        total = service.get_count()
        # Re-seed should not increase count for existing
        count2 = service.seed_from_json(data_path)
        assert service.get_count() == total

    def test_get_all_pagination(self, db_session):
        """Should paginate results."""
        service = ChemicalService(db_session)
        data_path = os.path.join(os.path.dirname(__file__), "..", "src", "data", "seed_chemicals.json")
        service.seed_from_json(data_path)

        page1 = service.get_all(page=1, per_page=5)
        assert len(page1) <= 5
