"""Chemicals API router."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from src.database import get_db
from src.services.chemical_service import ChemicalService

router = APIRouter(prefix="/chemicals", tags=["chemicals"])


@router.get("")
def list_chemicals(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all chemicals with pagination."""
    service = ChemicalService(db)
    chemicals = service.get_all(page=page, per_page=per_page, category=category)
    total = service.get_count()
    return {
        "chemicals": [c.to_dict() for c in chemicals],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.get("/search")
def search_chemicals(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    """Search chemicals by name, synonym, formula, or CAS."""
    service = ChemicalService(db)
    results = service.search(q)
    return {"chemicals": [c.to_dict() for c in results], "total": len(results)}


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    """Get all categories with counts."""
    service = ChemicalService(db)
    return {"categories": service.get_categories()}


@router.get("/{cas_number}")
def get_chemical(cas_number: str, db: Session = Depends(get_db)):
    """Get chemical by CAS number."""
    service = ChemicalService(db)
    chem = service.get_by_cas(cas_number)
    if not chem:
        raise HTTPException(status_code=404, detail="Chemical not found")
    return chem.to_dict()


@router.get("/{cas_number}/thresholds")
def get_thresholds(cas_number: str, db: Session = Depends(get_db)):
    """Get all thresholds for a chemical."""
    service = ChemicalService(db)
    thresholds = service.get_thresholds(cas_number)
    if not thresholds:
        raise HTTPException(status_code=404, detail="Chemical not found")
    return thresholds
