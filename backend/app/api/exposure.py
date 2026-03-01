from fastapi import APIRouter, HTTPException
from typing import List
from app.models.exposure import FinancialExposure
from app.services.exposure_engine import calculate_all_exposures, get_exposure_for_vendor

router = APIRouter()


@router.get("/vendors", response_model=List[FinancialExposure])
def get_all_vendor_exposures():
    """
    Returns financial exposure data for all vendors in the dataset.
    """
    exposures = calculate_all_exposures()
    if not exposures:
        raise HTTPException(status_code=404, detail="No vendor data found. Upload a dataset first.")
    return exposures


@router.get("/vendors/{vendor_id}", response_model=FinancialExposure)
def get_vendor_exposure(vendor_id: str):
    """
    Returns financial exposure data for a specific vendor.
    """
    exposure = get_exposure_for_vendor(vendor_id)
    if exposure is None:
        raise HTTPException(status_code=404, detail=f"Vendor '{vendor_id}' not found")
    return exposure
