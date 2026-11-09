import datetime
import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.shipment import Shipment, Document, ExtractedField, LineItem, AuditLog
from app.schemas.shipment import DocumentResponse
from app.services.extractor import VisionExtractorService
from app.services.cross_check_engine import CrossCheckEngine

router = APIRouter(prefix="/shipments/{id}/documents", tags=["Documents & Vision AI"])

@router.get("", response_model=List[DocumentResponse])
def list_shipment_documents(id: int, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.id == id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment.documents

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    id: int,
    file: UploadFile = File(...),
    doc_type: str = Form(..., description="commercial_invoice, packing_list, or bill_of_lading"),
    db: Session = Depends(get_db)
):
    shipment = db.query(Shipment).filter(Shipment.id == id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    # Save file to disk
    file_name = file.filename or f"doc_{doc_type}.pdf"
    file_path = settings.UPLOAD_DIR / f"{shipment.shipment_number}_{doc_type}_{file_name}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)

    # Create document record
    doc = Document(
        shipment_id=shipment.id,
        doc_type=doc_type,
        file_name=file_name,
        file_path=str(file_path),
        file_size=file_size,
        mime_type=file.content_type or "application/pdf",
        page_count=2,
        uploaded_at=datetime.datetime.utcnow()
    )
    db.add(doc)
    db.flush()

    db.query(ExtractedField).filter(ExtractedField.shipment_id == shipment.id).delete()
    db.query(LineItem).filter(LineItem.shipment_id == shipment.id).delete()
    db.flush()

    # Run Vision AI Extraction
    new_fields, new_items = VisionExtractorService.extract_document(shipment.id, doc)
    for f in new_fields:
        f.document_id = doc.id
        db.add(f)
    for item in new_items:
        db.add(item)
    db.flush()


    # Re-run Cross-Check validations
    for c in CrossCheckEngine.run_all_validations(shipment):
        db.add(c)

    # Update shipment status
    has_failed = any(c.status == "FAILED" for c in shipment.cross_checks)
    has_low_conf = any(f.is_low_confidence and not f.is_confirmed for f in shipment.extracted_fields)
    if has_failed:
        shipment.status = "Cross-Check Failed"
    elif has_low_conf:
        shipment.status = "Pending Review"
    else:
        shipment.status = "Cleared"

    # Log audit
    db.add(AuditLog(
        shipment_id=shipment.id,
        user_role="Documentation Executive",
        user_name="Documentation Executive",
        action="DOCUMENT_UPLOADED",
        details=f"Uploaded {doc_type} '{file_name}' ({file_size} bytes). Vision AI extracted {len(new_fields)} fields and {len(new_items)} line items."
    ))

    db.commit()
    db.refresh(doc)
    return doc
