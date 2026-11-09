import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.models.shipment import Shipment, ExtractedField, LineItem, CrossCheckResult, AuditLog
from app.schemas.shipment import (
    ShipmentListItem, 
    ShipmentDetailResponse, 
    ShipmentCreate, 
    ExtractedFieldUpdate, 
    ExtractedFieldResponse,
    LineItemUpdate,
    LineItemResponse
)
from app.services.cross_check_engine import CrossCheckEngine

router = APIRouter(prefix="/shipments", tags=["Shipments"])

@router.get("", response_model=List[ShipmentListItem])
def list_shipments(
    status: Optional[str] = Query(None, description="Filter by shipment status"),
    search: Optional[str] = Query(None, description="Search shipment #, supplier, or consignee"),
    db: Session = Depends(get_db)
):
    query = db.query(Shipment)

    if status and status != "All":
        if status == "Cleared":
            query = query.filter(or_(Shipment.status == "Cleared", Shipment.status == "Exported"))
        else:
            query = query.filter(Shipment.status == status)

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Shipment.shipment_number.ilike(search_pattern),
                Shipment.supplier_name.ilike(search_pattern),
                Shipment.consignee_name.ilike(search_pattern),
                Shipment.supplier_country.ilike(search_pattern)
            )
        )

    shipments = query.order_by(Shipment.created_at.desc()).all()

    items = []
    for s in shipments:
        doc_count = len(s.documents)
        low_conf = sum(1 for f in s.extracted_fields if f.is_low_confidence and not f.is_confirmed)
        has_failed_check = any(c.status == "FAILED" for c in s.cross_checks)
        cc_status = "Failed" if has_failed_check else ("Passed" if s.cross_checks else "Pending")

        items.append(ShipmentListItem(
            id=s.id,
            shipment_number=s.shipment_number,
            supplier_name=s.supplier_name,
            supplier_country=s.supplier_country,
            consignee_name=s.consignee_name,
            port_of_loading=s.port_of_loading,
            port_of_discharge=s.port_of_discharge,
            status=s.status,
            total_declared_value=s.total_declared_value,
            currency=s.currency,
            document_count=doc_count,
            low_confidence_count=low_conf,
            cross_check_status=cc_status,
            created_at=s.created_at,
            updated_at=s.updated_at
        ))
    return items

@router.get("/{id}", response_model=ShipmentDetailResponse)
def get_shipment_details(id: int, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.id == id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment

@router.post("", response_model=ShipmentDetailResponse)
def create_shipment(payload: ShipmentCreate, db: Session = Depends(get_db)):
    shipment = Shipment(**payload.dict())
    db.add(shipment)
    db.flush()

    # Log creation
    audit = AuditLog(
        shipment_id=shipment.id,
        user_role="Documentation Executive",
        user_name="John Doe",
        action="SHIPMENT_CREATED",
        details=f"Created shipment docket {shipment.shipment_number} for {shipment.supplier_name}."
    )
    db.add(audit)
    db.commit()
    db.refresh(shipment)
    return shipment

@router.patch("/{id}/fields/{field_id}", response_model=ExtractedFieldResponse)
def update_extracted_field(
    id: int, 
    field_id: int, 
    payload: ExtractedFieldUpdate, 
    db: Session = Depends(get_db)
):
    shipment = db.query(Shipment).filter(Shipment.id == id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    field = db.query(ExtractedField).filter(
        ExtractedField.id == field_id, 
        ExtractedField.shipment_id == id
    ).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    old_value = field.field_value
    field.field_value = payload.field_value
    field.is_confirmed = payload.is_confirmed
    field.confirmed_by = payload.confirmed_by
    if payload.is_confirmed:
        field.is_low_confidence = False

    # Sync back to shipment if key matching
    if field.field_key == "invoice_grand_total":
        try:
            shipment.total_declared_value = float(str(payload.field_value).replace(",", "").replace("$", ""))
        except ValueError:
            pass

    # Audit log
    audit = AuditLog(
        shipment_id=shipment.id,
        user_role="Documentation Executive",
        user_name=payload.confirmed_by or "Documentation Executive",
        action="FIELD_CONFIRMED" if payload.is_confirmed else "FIELD_UPDATED",
        details=f"Updated '{field.field_label}' from '{old_value}' to '{payload.field_value}' (Confirmed: {payload.is_confirmed})"
    )
    db.add(audit)

    # Re-evaluate deterministic cross-checks
    checks = CrossCheckEngine.run_all_validations(shipment)
    for c in checks:
        db.add(c)

    # Re-compute shipment status
    has_failed = any(c.status == "FAILED" for c in shipment.cross_checks)
    has_low_conf = any(f.is_low_confidence and not f.is_confirmed for f in shipment.extracted_fields)
    
    if has_failed:
        shipment.status = "Cross-Check Failed"
    elif has_low_conf:
        shipment.status = "Pending Review"
    else:
        shipment.status = "Cleared"

    shipment.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(field)
    return field

@router.patch("/{id}/line-items/{item_id}", response_model=LineItemResponse)
def update_line_item(
    id: int,
    item_id: int,
    payload: LineItemUpdate,
    db: Session = Depends(get_db)
):
    item = db.query(LineItem).filter(
        LineItem.id == item_id,
        LineItem.shipment_id == id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Line item not found")

    shipment = db.query(Shipment).filter(Shipment.id == id).first()

    update_dict = payload.dict(exclude_unset=True)
    for k, v in update_dict.items():
        setattr(item, k, v)

    # Recalculate total if qty or price changed
    if "quantity" in update_dict or "unit_price" in update_dict:
        item.total_amount = round(item.quantity * item.unit_price, 2)

    # Log audit
    db.add(AuditLog(
        shipment_id=shipment.id,
        user_role="Documentation Executive",
        user_name="Documentation Executive",
        action="LINE_ITEM_UPDATED",
        details=f"Item #{item.item_number} updated: {item.description} (HSN: {item.hsn_code}, Qty: {item.quantity}, Price: ${item.unit_price:.2f}, Total: ${item.total_amount:.2f})"
    ))

    # Re-run cross-checks
    for c in CrossCheckEngine.run_all_validations(shipment):
        db.add(c)

    has_failed = any(c.status == "FAILED" for c in shipment.cross_checks)
    if has_failed:
        shipment.status = "Cross-Check Failed"
    else:
        shipment.status = "Cleared"

    shipment.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(item)
    return item
