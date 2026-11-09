from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.shipment import Shipment, AuditLog
from app.schemas.shipment import AuditLogResponse

router = APIRouter(prefix="/shipments/{id}/audit-logs", tags=["Audit Trail"])

@router.get("", response_model=List[AuditLogResponse])
def get_audit_trail(id: int, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.id == id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    logs = db.query(AuditLog).filter(
        AuditLog.shipment_id == id
    ).order_by(AuditLog.timestamp.desc()).all()

    return logs
