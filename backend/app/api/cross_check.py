import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.shipment import Shipment, CrossCheckResult, AuditLog
from app.schemas.shipment import (
    CrossCheckSummary, 
    CrossCheckResultResponse, 
    ManagerOverrideRequest
)
from app.services.cross_check_engine import CrossCheckEngine

router = APIRouter(prefix="/shipments/{id}/cross-check", tags=["Cross-Check Engine"])

@router.get("", response_model=CrossCheckSummary)
def get_cross_check_summary(id: int, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.id == id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    checks = shipment.cross_checks or []
    total = len(checks)
    passed = sum(1 for c in checks if c.status == "PASSED")
    failed = sum(1 for c in checks if c.status == "FAILED")
    overridden = sum(1 for c in checks if c.status == "OVERRIDDEN")
    has_blocking = any(c.is_blocking and c.status == "FAILED" for c in checks)

    return CrossCheckSummary(
        total_rules=total,
        passed_rules=passed,
        failed_rules=failed,
        overridden_rules=overridden,
        has_blocking_discrepancy=has_blocking,
        is_export_ready=not has_blocking,
        results=checks
    )

@router.post("/run", response_model=CrossCheckSummary)
def run_cross_check(id: int, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.id == id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    updated_checks = CrossCheckEngine.run_all_validations(shipment)
    for c in updated_checks:
        db.add(c)

    has_failed = any(c.status == "FAILED" for c in shipment.cross_checks)
    if has_failed:
        shipment.status = "Cross-Check Failed"
    else:
        shipment.status = "Cleared"

    # Audit log
    db.add(AuditLog(
        shipment_id=shipment.id,
        user_role="System / CrossCheck Engine",
        user_name="RuleEngine-Deterministic",
        action="CROSS_CHECK_RE_EVALUATED",
        details=f"Cross-check re-evaluated. Status: {shipment.status}. Failed rules: {sum(1 for c in shipment.cross_checks if c.status == 'FAILED')}."
    ))

    db.commit()
    db.refresh(shipment)

    return get_cross_check_summary(id, db)

@router.post("/override", response_model=CrossCheckResultResponse)
def override_cross_check_rule(
    id: int,
    payload: ManagerOverrideRequest,
    db: Session = Depends(get_db)
):
    shipment = db.query(Shipment).filter(Shipment.id == id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    check = db.query(CrossCheckResult).filter(
        CrossCheckResult.shipment_id == id,
        CrossCheckResult.rule_code == payload.rule_code
    ).first()

    if not check:
        raise HTTPException(status_code=404, detail=f"Rule {payload.rule_code} not found on shipment")

    check.status = "OVERRIDDEN"
    check.is_blocking = False
    check.override_reason = payload.override_reason
    check.overridden_by = payload.manager_name
    check.overridden_at = datetime.datetime.utcnow()

    # Re-evaluate shipment overall status
    has_remaining_blockers = any(c.is_blocking and c.status == "FAILED" for c in shipment.cross_checks if c.id != check.id)
    if not has_remaining_blockers:
        shipment.status = "Cleared"

    # Audit log
    db.add(AuditLog(
        shipment_id=shipment.id,
        user_role="Documentation Manager",
        user_name=payload.manager_name,
        action="MANAGER_OVERRIDE_APPROVED",
        details=f"OVERRIDE APPLIED to {check.rule_name}. Reason: '{payload.override_reason}'"
    ))

    db.commit()
    db.refresh(check)
    return check
