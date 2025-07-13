"""
DICOM Routes

Medical imaging endpoints for the Amauta system.
"""

from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from typing import List

router = APIRouter()


class DICOMInfo(BaseModel):
    patient_id: str
    study_date: str
    modality: str
    description: str


@router.post("/upload")
async def upload_dicom(file: UploadFile = File(...)):
    """Upload DICOM file"""
    return {"message": f"Uploaded DICOM file: {file.filename}"}


@router.get("/studies", response_model=List[DICOMInfo])
async def get_studies():
    """Get all DICOM studies"""
    return [DICOMInfo(patient_id="12345", study_date="2024-01-15", modality="CT", description="Chest CT scan")]


@router.get("/view/{study_id}")
async def view_study(study_id: str):
    """View DICOM study"""
    return {"study_id": study_id, "status": "loaded"}
