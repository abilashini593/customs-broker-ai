import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.shipment import Shipment, AuditLog
from app.schemas.shipment import ExportRequest
from app.services.exporter import CustomsFilingExporter

router = APIRouter(prefix="/shipments/{id}/export", tags=["Customs Filing Export"])

@router.post("")
def export_shipment_filing(
    id: int,
    payload: ExportRequest,
    db: Session = Depends(get_db)
):
    shipment = db.query(Shipment).filter(Shipment.id == id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    # Strict compliance check: Are there any blocking failures?
    blocking_checks = [c for c in shipment.cross_checks if c.is_blocking and c.status == "FAILED"]
    if blocking_checks:
        reasons = [f"[{c.rule_code}] {c.message}" for c in blocking_checks]
        raise HTTPException(
            status_code=400,
            detail={
                "error": "EXPORT_BLOCKED",
                "message": f"Export blocked by {len(blocking_checks)} deterministic cross-check failure(s). Must be resolved or overridden by Documentation Manager.",
                "blocking_rules": reasons
            }
        )

    # Generate Customs Filing Export with selected format
    file_path, file_name, preview_content = CustomsFilingExporter.generate_filing_export(
        shipment=shipment,
        user_role=payload.user_role,
        user_name=payload.user_name,
        format=payload.format
    )

    # Update shipment status
    shipment.status = "Exported"

    # Audit log
    db.add(AuditLog(
        shipment_id=shipment.id,
        user_role=payload.user_role,
        user_name=payload.user_name,
        action="CUSTOMS_EXPORT_GENERATED",
        details=f"Generated customs filing manifest '{file_name}' for system '{payload.system_target}'. Format: {payload.format.upper()}."
    ))
    db.commit()

    return {
        "success": True,
        "shipment_id": shipment.id,
        "shipment_number": shipment.shipment_number,
        "file_name": file_name,
        "download_url": f"/api/shipments/{shipment.id}/export/download/{file_name}",
        "format": payload.format,
        "preview_content": preview_content,
        "system_target": payload.system_target,
        "total_line_items": len(shipment.line_items),
        "total_declared_value": shipment.total_declared_value,
        "currency": shipment.currency
    }

@router.get("/download/{file_name}")
def download_export_file(id: int, file_name: str, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.id == id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    from app.core.config import settings
    file_path = settings.EXPORT_DIR / file_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Export file not found")

    if file_name.endswith(".xlsx"):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        media_type = "text/csv"

    # Read binary content directly into memory to avoid stream chunking corruption in Excel
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    return Response(
        content=file_bytes,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{file_name}"',
            "Content-Length": str(len(file_bytes))
        }
    )