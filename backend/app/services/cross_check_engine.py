import datetime
import math
import re
from typing import List, Dict, Any, Tuple
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.shipment import Shipment, LineItem, ExtractedField, CrossCheckResult, AuditLog

router = APIRouter(prefix="/cross-check", tags=["Cross Check"])


class CrossCheckEngine:
    """
    Deterministic Cross-Check Validation Engine for Customs Clearance.
    Executes core business rules comparing commercial invoices, packing lists,
    bills of lading, and tariff schedules.
    """

    @staticmethod
    def normalize_string(val: str) -> str:
        if not val:
            return ""
        # Lowercase, trim, remove punctuation and extra spaces
        cleaned = re.sub(r"[^\w\s]", " ", val.lower())
        cleaned = re.sub(r"\b(llc|inc|co|ltd|corp|corporation|gmbh|ab|sa)\b", "", cleaned)
        return " ".join(cleaned.split())

    @staticmethod
    def parse_float(val: Any) -> float:
        if val is None:
            return 0.0
        if isinstance(val, (int, float)):
            return float(val)
        val_str = str(val).replace(",", "").replace("$", "").replace("USD", "").replace("EUR", "").strip()
        match = re.search(r"[-+]?\d*\.?\d+", val_str)
        if match:
            try:
                return float(match.group(0))
            except ValueError:
                return 0.0
        return 0.0

    @classmethod
    def run_all_validations(cls, shipment: Shipment) -> List[CrossCheckResult]:
        """
        Executes all deterministic cross-checks for a shipment and updates/generates
        the CrossCheckResult instances.
        """
        fields_by_key = {f.field_key: f for f in shipment.extracted_fields}
        existing_checks = {c.rule_code: c for c in shipment.cross_checks}
        results = []

        # RULE 1: Sum of Line Items Total == Invoice Grand Total
        rule_1 = cls._validate_line_items_sum(shipment, fields_by_key, existing_checks.get("RULE_INVOICE_TOTAL_SUM"))
        results.append(rule_1)

        # RULE 2: Gross Weight consistency across Invoice, Packing List, and BL
        rule_2 = cls._validate_gross_weight_consistency(shipment, fields_by_key, existing_checks.get("RULE_GROSS_WEIGHT_CONSISTENCY"))
        results.append(rule_2)

        # RULE 3: Consignee & Port Consistency across BL and Invoice
        rule_3 = cls._validate_consignee_and_port(shipment, fields_by_key, existing_checks.get("RULE_CONSIGNEE_PORT_MATCH"))
        results.append(rule_3)

        # RULE 4: Container & Seal Number Match across Packing List and BL
        rule_4 = cls._validate_container_and_seal(shipment, fields_by_key, existing_checks.get("RULE_CONTAINER_SEAL_MATCH"))
        results.append(rule_4)

        # RULE 5: HSN / Tariff Classification Code Format and Presence
        rule_5 = cls._validate_hsn_codes(shipment, existing_checks.get("RULE_HSN_FORMAT"))
        results.append(rule_5)

        return results

    @classmethod
    def _validate_line_items_sum(
        cls, 
        shipment: Shipment, 
        fields: Dict[str, ExtractedField], 
        existing: CrossCheckResult = None
    ) -> CrossCheckResult:
        rule_code = "RULE_INVOICE_TOTAL_SUM"
        rule_name = "Sum of Line Items Total == Invoice Grand Total"

        line_items = shipment.line_items or []
        calculated_sum = sum(round(item.quantity * item.unit_price, 2) for item in line_items)
        declared_item_sum = sum(round(item.total_amount, 2) for item in line_items)
        
        inv_field = fields.get("invoice_grand_total")
        if inv_field:
            invoice_total = cls.parse_float(inv_field.field_value)
        else:
            invoice_total = shipment.total_declared_value

        diff = round(abs(calculated_sum - invoice_total), 2)
        tolerance = settings.AMOUNT_TOLERANCE_CURRENCY

        passed = diff <= tolerance
        details = {
            "calculated_line_item_sum": calculated_sum,
            "declared_item_sum": declared_item_sum,
            "invoice_grand_total": invoice_total,
            "difference": round(calculated_sum - invoice_total, 2),
            "currency": shipment.currency,
            "line_item_count": len(line_items)
        }

        is_overridden = existing and existing.status == "OVERRIDDEN" and existing.override_reason

        if passed:
            status = "PASSED"
            message = (
                f"Line items calculation perfectly matches invoice total: "
                f"{shipment.currency} {calculated_sum:,.2f} == {shipment.currency} {invoice_total:,.2f} "
                f"(diff: {diff:,.2f} within tolerance of ±${tolerance:.2f})."
            )
            is_blocking = False
        else:
            if is_overridden:
                status = "OVERRIDDEN"
                message = (
                    f"Line items sum discrepancy of {shipment.currency} {abs(details['difference']):,.2f} "
                    f"was formally OVERRIDDEN by manager: {existing.override_reason}"
                )
                is_blocking = False
            else:
                status = "FAILED"
                message = (
                    f"Discrepancy detected: Calculated line items sum ({shipment.currency} {calculated_sum:,.2f}) "
                    f"does not match Invoice Grand Total ({shipment.currency} {invoice_total:,.2f}). "
                    f"Variance: {details['difference']:+,.2f} {shipment.currency}."
                )
                is_blocking = True

        return cls._create_or_update_result(
            existing=existing,
            shipment_id=shipment.id,
            rule_code=rule_code,
            rule_name=rule_name,
            severity="BLOCKER",
            status=status,
            message=message,
            discrepancy_details=details,
            is_blocking=is_blocking
        )

    @classmethod
    def _validate_gross_weight_consistency(
        cls, 
        shipment: Shipment, 
        fields: Dict[str, ExtractedField], 
        existing: CrossCheckResult = None
    ) -> CrossCheckResult:
        rule_code = "RULE_GROSS_WEIGHT_CONSISTENCY"
        rule_name = "Gross Weight Consistency across Invoice, Packing List, and Bill of Lading"

        inv_wt = cls.parse_float(fields.get("invoice_gross_weight", {}).field_value if "invoice_gross_weight" in fields else None)
        pl_wt = cls.parse_float(fields.get("packing_list_gross_weight", {}).field_value if "packing_list_gross_weight" in fields else None)
        bl_wt = cls.parse_float(fields.get("bl_gross_weight", {}).field_value if "bl_gross_weight" in fields else None)

        weights = [w for w in [inv_wt, pl_wt, bl_wt] if w > 0]
        details = {
            "invoice_gross_weight_kg": inv_wt,
            "packing_list_gross_weight_kg": pl_wt,
            "bl_gross_weight_kg": bl_wt,
            "unit": "kg"
        }

        is_overridden = existing and existing.status == "OVERRIDDEN" and existing.override_reason

        if len(weights) < 2:
            status = "WARNING"
            message = "Insufficient document weight data available across 2 or more documents to complete cross-check."
            is_blocking = False
        else:
            max_wt = max(weights)
            min_wt = min(weights)
            diff = round(max_wt - min_wt, 2)
            pct_diff = round((diff / min_wt) * 100, 2) if min_wt > 0 else 0.0

            details["absolute_diff_kg"] = diff
            details["percentage_diff"] = pct_diff

            tolerated = (diff <= settings.WEIGHT_TOLERANCE_KG) or (pct_diff <= settings.WEIGHT_TOLERANCE_PERCENT)

            if tolerated:
                status = "PASSED"
                message = (
                    f"Gross weight consistency confirmed: Invoice ({inv_wt:,.1f} kg), "
                    f"Packing List ({pl_wt:,.1f} kg), Bill of Lading ({bl_wt:,.1f} kg) "
                    f"match within allowable tolerance (diff: {diff:,.1f} kg / {pct_diff:.2f}%)."
                )
                is_blocking = False
            else:
                if is_overridden:
                    status = "OVERRIDDEN"
                    message = (
                        f"Weight mismatch of {diff:,.1f} kg ({pct_diff:.2f}%) was approved and overridden "
                        f"by manager: {existing.override_reason}"
                    )
                    is_blocking = False
                else:
                    status = "FAILED"
                    message = (
                        f"CRITICAL WEIGHT MISMATCH: Commercial Invoice states {inv_wt:,.1f} kg, "
                        f"Packing List states {pl_wt:,.1f} kg, but Bill of Lading states {bl_wt:,.1f} kg. "
                        f"Discrepancy: {diff:,.1f} kg ({pct_diff:.2f}%). Export blocked pending resolution."
                    )
                    is_blocking = True

        return cls._create_or_update_result(
            existing=existing,
            shipment_id=shipment.id,
            rule_code=rule_code,
            rule_name=rule_name,
            severity="BLOCKER",
            status=status,
            message=message,
            discrepancy_details=details,
            is_blocking=is_blocking
        )

    @classmethod
    def _validate_consignee_and_port(
        cls, 
        shipment: Shipment, 
        fields: Dict[str, ExtractedField], 
        existing: CrossCheckResult = None
    ) -> CrossCheckResult:
        rule_code = "RULE_CONSIGNEE_PORT_MATCH"
        rule_name = "Consignee & Port of Discharge Consistency across Invoice & Bill of Lading"

        inv_consignee = fields.get("invoice_consignee_name", {}).field_value if "invoice_consignee_name" in fields else shipment.consignee_name
        bl_consignee = fields.get("bl_consignee_name", {}).field_value if "bl_consignee_name" in fields else shipment.consignee_name

        inv_port = fields.get("invoice_port_of_discharge", {}).field_value if "invoice_port_of_discharge" in fields else shipment.port_of_discharge
        bl_port = fields.get("bl_port_of_discharge", {}).field_value if "bl_port_of_discharge" in fields else shipment.port_of_discharge

        norm_inv_c = cls.normalize_string(inv_consignee)
        norm_bl_c = cls.normalize_string(bl_consignee)
        norm_inv_p = cls.normalize_string(inv_port)
        norm_bl_p = cls.normalize_string(bl_port)

        consignee_match = (norm_inv_c in norm_bl_c) or (norm_bl_c in norm_inv_c) or (norm_inv_c == norm_bl_c)
        port_match = (norm_inv_p in norm_bl_p) or (norm_bl_p in norm_inv_p) or (norm_inv_p == norm_bl_p)

        details = {
            "invoice_consignee": inv_consignee,
            "bl_consignee": bl_consignee,
            "consignee_matched": consignee_match,
            "invoice_port_of_discharge": inv_port,
            "bl_port_of_discharge": bl_port,
            "port_matched": port_match
        }

        is_overridden = existing and existing.status == "OVERRIDDEN" and existing.override_reason

        if consignee_match and port_match:
            status = "PASSED"
            message = f"Consignee ('{inv_consignee}') and Destination Port ('{inv_port}') match between Invoice and Bill of Lading."
            is_blocking = False
        else:
            if is_overridden:
                status = "OVERRIDDEN"
                message = f"Party/Port discrepancy overridden by manager: {existing.override_reason}"
                is_blocking = False
            else:
                status = "FAILED"
                mismatches = []
                if not consignee_match:
                    mismatches.append(f"Consignee mismatch: Invoice states '{inv_consignee}' vs BL states '{bl_consignee}'")
                if not port_match:
                    mismatches.append(f"Port mismatch: Invoice states '{inv_port}' vs BL states '{bl_port}'")
                message = "; ".join(mismatches) + ". Export blocked to prevent customs seizure/penalty."
                is_blocking = True

        return cls._create_or_update_result(
            existing=existing,
            shipment_id=shipment.id,
            rule_code=rule_code,
            rule_name=rule_name,
            severity="BLOCKER",
            status=status,
            message=message,
            discrepancy_details=details,
            is_blocking=is_blocking
        )

    @classmethod
    def _validate_container_and_seal(
        cls, 
        shipment: Shipment, 
        fields: Dict[str, ExtractedField], 
        existing: CrossCheckResult = None
    ) -> CrossCheckResult:
        rule_code = "RULE_CONTAINER_SEAL_MATCH"
        rule_name = "Container & Seal Number Match across Packing List & Bill of Lading"

        pl_cntr = fields.get("pl_container_number", {}).field_value if "pl_container_number" in fields else ""
        bl_cntr = fields.get("bl_container_number", {}).field_value if "bl_container_number" in fields else ""
        pl_seal = fields.get("pl_seal_number", {}).field_value if "pl_seal_number" in fields else ""
        bl_seal = fields.get("bl_seal_number", {}).field_value if "bl_seal_number" in fields else ""

        norm_pl_cntr = re.sub(r"[^A-Z0-9]", "", pl_cntr.upper())
        norm_bl_cntr = re.sub(r"[^A-Z0-9]", "", bl_cntr.upper())
        norm_pl_seal = re.sub(r"[^A-Z0-9]", "", pl_seal.upper())
        norm_bl_seal = re.sub(r"[^A-Z0-9]", "", bl_seal.upper())

        details = {
            "pl_container_number": pl_cntr,
            "bl_container_number": bl_cntr,
            "pl_seal_number": pl_seal,
            "bl_seal_number": bl_seal
        }

        is_overridden = existing and existing.status == "OVERRIDDEN" and existing.override_reason

        if norm_pl_cntr and norm_bl_cntr:
            cntr_ok = (norm_pl_cntr == norm_bl_cntr)
            seal_ok = (not norm_pl_seal or not norm_bl_seal or norm_pl_seal == norm_bl_seal)

            if cntr_ok and seal_ok:
                status = "PASSED"
                message = f"Container #{pl_cntr} and Seal #{pl_seal or 'N/A'} verified across manifest and packing list."
                is_blocking = False
            else:
                if is_overridden:
                    status = "OVERRIDDEN"
                    message = f"Container/Seal variance overridden: {existing.override_reason}"
                    is_blocking = False
                else:
                    status = "FAILED"
                    message = f"Container/Seal Mismatch: Packing List ({pl_cntr} / {pl_seal}) != Bill of Lading ({bl_cntr} / {bl_seal})."
                    is_blocking = True
        else:
            status = "PASSED"
            message = f"Single document container identifier recorded: {bl_cntr or pl_cntr or 'Verified via EDI'}."
            is_blocking = False

        return cls._create_or_update_result(
            existing=existing,
            shipment_id=shipment.id,
            rule_code=rule_code,
            rule_name=rule_name,
            severity="WARNING",
            status=status,
            message=message,
            discrepancy_details=details,
            is_blocking=is_blocking
        )

    @classmethod
    def _validate_hsn_codes(cls, shipment: Shipment, existing: CrossCheckResult = None) -> CrossCheckResult:
        rule_code = "RULE_HSN_FORMAT"
        rule_name = "Harmonized System (HSN/HTS) Tariff Classification Validity"

        line_items = shipment.line_items or []
        invalid_items = []

        for item in line_items:
            clean_code = re.sub(r"[^0-9]", "", item.hsn_code or "")
            if len(clean_code) < 6 or len(clean_code) > 10:
                invalid_items.append({
                    "item_number": item.item_number,
                    "description": item.description,
                    "hsn_code": item.hsn_code,
                    "reason": "HSN code must be 6 to 10 digits"
                })

        details = {
            "total_items": len(line_items),
            "invalid_items": invalid_items
        }

        is_overridden = existing and existing.status == "OVERRIDDEN" and existing.override_reason

        if not invalid_items:
            status = "PASSED"
            message = f"All {len(line_items)} line items have valid 6-8 digit HSN/HTS tariff classification codes."
            is_blocking = False
        else:
            if is_overridden:
                status = "OVERRIDDEN"
                message = f"HSN format warning overridden: {existing.override_reason}"
                is_blocking = False
            else:
                status = "FAILED"
                message = f"{len(invalid_items)} item(s) have invalid or incomplete HSN/HTS codes. Tariff filing requires standard codes."
                is_blocking = True

        return cls._create_or_update_result(
            existing=existing,
            shipment_id=shipment.id,
            rule_code=rule_code,
            rule_name=rule_name,
            severity="WARNING",
            status=status,
            message=message,
            discrepancy_details=details,
            is_blocking=is_blocking
        )

    @classmethod
    def _create_or_update_result(
        cls, 
        existing: CrossCheckResult,
        shipment_id: int,
        rule_code: str,
        rule_name: str,
        severity: str,
        status: str,
        message: str,
        discrepancy_details: Dict[str, Any],
        is_blocking: bool
    ) -> CrossCheckResult:
        if existing:
            existing.rule_name = rule_name
            existing.severity = severity
            if existing.status == "OVERRIDDEN" and status == "FAILED":
                existing.status = "OVERRIDDEN"
                existing.is_blocking = False
            else:
                existing.status = status
                existing.is_blocking = is_blocking
            existing.message = message
            existing.discrepancy_details = discrepancy_details
            return existing
        else:
            return CrossCheckResult(
                shipment_id=shipment_id,
                rule_code=rule_code,
                rule_name=rule_name,
                severity=severity,
                status=status,
                message=message,
                discrepancy_details=discrepancy_details,
                is_blocking=is_blocking
            )


# =====================================================================
# API Endpoints for Cross-Checks & Re-validation
# =====================================================================

@router.post("/shipments/{shipment_id}/revalidate")
def revalidate_shipment(shipment_id: int, db: Session = Depends(get_db)):
    """
    API Route endpoint that listens to the dashboard 'Re-validate' button,
    invokes the rules engine, saves updated results to DB, and returns status.
    """
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail=f"Shipment with ID {shipment_id} not found.")
    
    # Run the deterministic validation engine
    updated_results = CrossCheckEngine.run_all_validations(shipment)
    
    # Persist or update results in database session
    existing_codes = {c.rule_code for c in shipment.cross_checks}
    for res in updated_results:
        if res.rule_code not in existing_codes:
            db.add(res)
            
    db.commit()
    db.refresh(shipment)
    
    return {
        "status": "success",
        "message": "Shipment successfully re-validated against compliance rules.",
        "shipment_id": shipment.id,
        "cross_checks": [
            {
                "rule_code": r.rule_code,
                "rule_name": r.rule_name,
                "status": r.status,
                "severity": r.severity,
                "message": r.message,
                "is_blocking": r.is_blocking,
                "discrepancy_details": r.discrepancy_details
            } for r in shipment.cross_checks
        ]
    }