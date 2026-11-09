import pytest
from app.models.shipment import Shipment, LineItem, ExtractedField, CrossCheckResult
from app.services.cross_check_engine import CrossCheckEngine

def create_mock_shipment(
    invoice_total=100000.0,
    items=None,
    invoice_wt="12000.0",
    pl_wt="12000.0",
    bl_wt="12000.0",
    inv_consignee="Apex Logistics Global LLC",
    bl_consignee="Apex Logistics Global Inc",
    hsn_codes=None
):
    shipment = Shipment(
        id=999,
        shipment_number="SHP-TEST-001",
        supplier_name="Test Electronics Ltd.",
        supplier_country="China",
        consignee_name="Apex Logistics Global LLC",
        consignee_country="United States",
        port_of_loading="Shenzhen, CN",
        port_of_discharge="Los Angeles, US",
        total_declared_value=invoice_total,
        currency="USD",
        status="Pending Review"
    )

    if items is None:
        items = [
            LineItem(
                id=1, shipment_id=999, item_number=1,
                description="Controller IC", hsn_code=hsn_codes[0] if hsn_codes else "8542.31.00",
                quantity=1000.0, unit="PCS", unit_price=50.0, total_amount=50000.0,
                currency="USD"
            ),
            LineItem(
                id=2, shipment_id=999, item_number=2,
                description="Power Transistors", hsn_code=hsn_codes[1] if hsn_codes else "8541.29.00",
                quantity=2000.0, unit="PCS", unit_price=25.0, total_amount=50000.0,
                currency="USD"
            )
        ]
    shipment.line_items = items

    fields = [
        ExtractedField(id=1, shipment_id=999, field_group="valuation", field_key="invoice_grand_total", field_label="Invoice Total", field_value=str(invoice_total)),
        ExtractedField(id=2, shipment_id=999, field_group="weights", field_key="invoice_gross_weight", field_label="Inv Gross Wt", field_value=invoice_wt),
        ExtractedField(id=3, shipment_id=999, field_group="weights", field_key="packing_list_gross_weight", field_label="PL Gross Wt", field_value=pl_wt),
        ExtractedField(id=4, shipment_id=999, field_group="weights", field_key="bl_gross_weight", field_label="BL Gross Wt", field_value=bl_wt),
        ExtractedField(id=5, shipment_id=999, field_group="parties", field_key="invoice_consignee_name", field_label="Inv Consignee", field_value=inv_consignee),
        ExtractedField(id=6, shipment_id=999, field_group="parties", field_key="bl_consignee_name", field_label="BL Consignee", field_value=bl_consignee),
    ]
    shipment.extracted_fields = fields
    shipment.cross_checks = []
    return shipment


class TestCrossCheckEngine:

    def test_line_items_sum_exact_match(self):
        """Rule 1: Line items sum ($50k + $50k) matches Invoice Grand Total ($100k)"""
        shipment = create_mock_shipment(invoice_total=100000.0)
        results = CrossCheckEngine.run_all_validations(shipment)
        rule_1 = next(r for r in results if r.rule_code == "RULE_INVOICE_TOTAL_SUM")

        assert rule_1.status == "PASSED"
        assert not rule_1.is_blocking
        assert rule_1.discrepancy_details["difference"] == 0.0

    def test_line_items_sum_mismatch_fails_and_blocks(self):
        """Rule 1: Line items sum ($100k) does not match invoice total ($105k) -> FAILS and BLOCKS"""
        shipment = create_mock_shipment(invoice_total=105000.0) # $5,000 difference
        results = CrossCheckEngine.run_all_validations(shipment)
        rule_1 = next(r for r in results if r.rule_code == "RULE_INVOICE_TOTAL_SUM")

        assert rule_1.status == "FAILED"
        assert rule_1.is_blocking is True
        assert rule_1.discrepancy_details["difference"] == -5000.0
        assert "Discrepancy detected" in rule_1.message

    def test_line_items_rounding_tolerance_passes(self):
        """Rule 1: Small $0.04 rounding difference within $0.10 tolerance passes"""
        shipment = create_mock_shipment(invoice_total=100000.04)
        results = CrossCheckEngine.run_all_validations(shipment)
        rule_1 = next(r for r in results if r.rule_code == "RULE_INVOICE_TOTAL_SUM")

        assert rule_1.status == "PASSED"
        assert not rule_1.is_blocking

    def test_gross_weight_matching_exact(self):
        """Rule 2: All three documents have matching gross weight (12,000 kg)"""
        shipment = create_mock_shipment(invoice_wt="12000.0", pl_wt="12000.0", bl_wt="12000.0")
        results = CrossCheckEngine.run_all_validations(shipment)
        rule_2 = next(r for r in results if r.rule_code == "RULE_GROSS_WEIGHT_CONSISTENCY")

        assert rule_2.status == "PASSED"
        assert not rule_2.is_blocking
        assert rule_2.discrepancy_details["absolute_diff_kg"] == 0.0

    def test_gross_weight_mismatch_fails_and_blocks(self):
        """Rule 2: Invoice=12,450 kg vs BL=12,800 kg (+350 kg variance) -> FAILS and BLOCKS"""
        shipment = create_mock_shipment(invoice_wt="12450.0", pl_wt="12450.0", bl_wt="12800.0")
        results = CrossCheckEngine.run_all_validations(shipment)
        rule_2 = next(r for r in results if r.rule_code == "RULE_GROSS_WEIGHT_CONSISTENCY")

        assert rule_2.status == "FAILED"
        assert rule_2.is_blocking is True
        assert rule_2.discrepancy_details["absolute_diff_kg"] == 350.0
        assert rule_2.discrepancy_details["percentage_diff"] == pytest.approx(2.81, rel=1e-2)
        assert "CRITICAL WEIGHT MISMATCH" in rule_2.message

    def test_gross_weight_within_tolerance_passes(self):
        """Rule 2: Difference within 4 kg (<= 5 kg absolute tolerance) passes cleanly"""
        shipment = create_mock_shipment(invoice_wt="12000.0", pl_wt="12002.0", bl_wt="12003.5")
        results = CrossCheckEngine.run_all_validations(shipment)
        rule_2 = next(r for r in results if r.rule_code == "RULE_GROSS_WEIGHT_CONSISTENCY")

        assert rule_2.status == "PASSED"
        assert not rule_2.is_blocking

    def test_manager_override_unblocks_rule(self):
        """Manager override preserves override status and unblocks export"""
        shipment = create_mock_shipment(invoice_wt="12450.0", pl_wt="12450.0", bl_wt="12800.0")
        
        # Pre-existing override
        existing_check = CrossCheckResult(
            shipment_id=999,
            rule_code="RULE_GROSS_WEIGHT_CONSISTENCY",
            rule_name="Weight Consistency",
            severity="BLOCKER",
            status="OVERRIDDEN",
            message="Prior override",
            is_blocking=False,
            override_reason="Tare weight of 4 steel pallets verified by carrier weight certificate.",
            overridden_by="Sarah Chen (Documentation Manager)"
        )
        shipment.cross_checks = [existing_check]

        results = CrossCheckEngine.run_all_validations(shipment)
        rule_2 = next(r for r in results if r.rule_code == "RULE_GROSS_WEIGHT_CONSISTENCY")

        assert rule_2.status == "OVERRIDDEN"
        assert rule_2.is_blocking is False
        assert "Tare weight of 4 steel pallets" in rule_2.message

    def test_consignee_entity_matching(self):
        """Rule 3: Matches consignee regardless of corporate suffix (LLC vs Inc)"""
        shipment = create_mock_shipment(
            inv_consignee="Apex Logistics Global LLC",
            bl_consignee="Apex Logistics Global Inc"
        )
        results = CrossCheckEngine.run_all_validations(shipment)
        rule_3 = next(r for r in results if r.rule_code == "RULE_CONSIGNEE_PORT_MATCH")

        assert rule_3.status == "PASSED"
        assert not rule_3.is_blocking

    def test_consignee_mismatch_blocks_export(self):
        """Rule 3: Completely different consignees fail and block export"""
        shipment = create_mock_shipment(
            inv_consignee="Apex Logistics Global LLC",
            bl_consignee="Totally Different Importer Corp"
        )
        results = CrossCheckEngine.run_all_validations(shipment)
        rule_3 = next(r for r in results if r.rule_code == "RULE_CONSIGNEE_PORT_MATCH")

        assert rule_3.status == "FAILED"
        assert rule_3.is_blocking is True
        assert "Consignee mismatch" in rule_3.message

    def test_hsn_code_validation_success_and_failure(self):
        """Rule 5: Validates tariff classification format (6 to 10 digits)"""
        # Valid HSNs
        shipment_valid = create_mock_shipment(hsn_codes=["8542.31.00", "8541.29.00"])
        results_valid = CrossCheckEngine.run_all_validations(shipment_valid)
        rule_5_valid = next(r for r in results_valid if r.rule_code == "RULE_HSN_FORMAT")
        assert rule_5_valid.status == "PASSED"

        # Invalid HSN (only 3 digits)
        shipment_invalid = create_mock_shipment(hsn_codes=["854", "8541.29.00"])
        results_invalid = CrossCheckEngine.run_all_validations(shipment_invalid)
        rule_5_invalid = next(r for r in results_invalid if r.rule_code == "RULE_HSN_FORMAT")
        assert rule_5_invalid.status == "FAILED"
        assert rule_5_invalid.is_blocking is True
