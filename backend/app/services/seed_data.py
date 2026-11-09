import datetime
from sqlalchemy.orm import Session
from app.models.shipment import Shipment, Document, ExtractedField, LineItem, CrossCheckResult, AuditLog
from app.services.cross_check_engine import CrossCheckEngine

def seed_database(db: Session):
    """
    Populates database with realistic customs brokerage shipments,
    documents, extracted fields, cross-check results, and audit trails.
    """
    if db.query(Shipment).first():
        print("Database already contains data, skipping seed.")
        return

    print("Seeding database with realistic customs brokerage data...")

    # =========================================================================
    # SHIPMENT 1: Shenzhen Precision Microelectronics (Cross-Check Failed)
    # =========================================================================
    shp1 = Shipment(
        shipment_number="SHP-2026-8942",
        supplier_name="Shenzhen Precision Microelectronics Co., Ltd.",
        supplier_country="China",
        consignee_name="Apex Logistics Global LLC",
        consignee_country="United States",
        port_of_loading="Yantian (Shenzhen), CN",
        port_of_discharge="Port of Los Angeles, US",
        vessel_name="EVER GIVEN",
        voyage_number="0428-091W",
        status="Cross-Check Failed",
        total_declared_value=142500.00,
        currency="USD",
        notes="High-priority semiconductor shipment. Gross weight variance detected between Bill of Lading and Packing List.",
        created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=6),
        updated_at=datetime.datetime.utcnow() - datetime.timedelta(minutes=45)
    )
    db.add(shp1)
    db.flush()

    # Documents for Shipment 1
    doc1_inv = Document(
        shipment_id=shp1.id,
        doc_type="commercial_invoice",
        file_name="COMMERCIAL_INVOICE_INV-8841.pdf",
        file_path="uploads/COMMERCIAL_INVOICE_INV-8841.pdf",
        file_size=245800,
        mime_type="application/pdf",
        page_count=2,
        uploaded_at=shp1.created_at
    )
    doc1_pl = Document(
        shipment_id=shp1.id,
        doc_type="packing_list",
        file_name="PACKING_LIST_PL-8841.pdf",
        file_path="uploads/PACKING_LIST_PL-8841.pdf",
        file_size=189400,
        mime_type="application/pdf",
        page_count=2,
        uploaded_at=shp1.created_at
    )
    doc1_bl = Document(
        shipment_id=shp1.id,
        doc_type="bill_of_lading",
        file_name="OCEAN_BILL_OF_LADING_MAEU-92837190.pdf",
        file_path="uploads/OCEAN_BILL_OF_LADING_MAEU-92837190.pdf",
        file_size=312000,
        mime_type="application/pdf",
        page_count=1,
        uploaded_at=shp1.created_at
    )
    db.add_all([doc1_inv, doc1_pl, doc1_bl])
    db.flush()

    # Extracted fields for Shipment 1
    fields_shp1 = [
        # Invoice fields
        ExtractedField(
            shipment_id=shp1.id, document_id=doc1_inv.id, field_group="metadata",
            field_key="invoice_number", field_label="Invoice Number",
            field_value="INV-2026-CN-8841", raw_value="INV-2026-CN-8841",
            confidence_score=99.2, is_low_confidence=False, is_confirmed=True,
            bounding_box={"page": 1, "x": 72, "y": 140, "w": 180, "h": 22}
        ),
        ExtractedField(
            shipment_id=shp1.id, document_id=doc1_inv.id, field_group="metadata",
            field_key="invoice_date", field_label="Invoice Date",
            field_value="2026-10-18", raw_value="18/10/2026",
            confidence_score=95.1, is_low_confidence=False, is_confirmed=True,
            bounding_box={"page": 1, "x": 72, "y": 168, "w": 140, "h": 20}
        ),
        ExtractedField(
            shipment_id=shp1.id, document_id=doc1_inv.id, field_group="parties",
            field_key="invoice_supplier_name", field_label="Exporter / Shipper",
            field_value="Shenzhen Precision Microelectronics Co., Ltd.",
            raw_value="Shenzhen Precision Microelectronics Co., Ltd.",
            confidence_score=98.8, is_low_confidence=False, is_confirmed=True,
            bounding_box={"page": 1, "x": 72, "y": 80, "w": 310, "h": 28}
        ),
        ExtractedField(
            shipment_id=shp1.id, document_id=doc1_inv.id, field_group="parties",
            field_key="invoice_consignee_name", field_label="Consignee / Importer",
            field_value="Apex Logistics Global LLC", raw_value="Apex Logistics Global LLC",
            confidence_score=97.4, is_low_confidence=False, is_confirmed=True,
            bounding_box={"page": 1, "x": 420, "y": 80, "w": 280, "h": 28}
        ),
        ExtractedField(
            shipment_id=shp1.id, document_id=doc1_inv.id, field_group="metadata",
            field_key="invoice_port_of_discharge", field_label="Port of Discharge",
            field_value="Port of Los Angeles, US", raw_value="Port of Los Angeles, US",
            confidence_score=96.0, is_low_confidence=False, is_confirmed=True,
            bounding_box={"page": 1, "x": 420, "y": 195, "w": 220, "h": 22}
        ),
        ExtractedField(
            shipment_id=shp1.id, document_id=doc1_inv.id, field_group="weights",
            field_key="invoice_gross_weight", field_label="Invoice Gross Weight (kg)",
            field_value="12450.00", raw_value="12,450.00 KGS",
            confidence_score=97.8, is_low_confidence=False, is_confirmed=True,
            bounding_box={"page": 1, "x": 420, "y": 510, "w": 160, "h": 24}
        ),
        ExtractedField(
            shipment_id=shp1.id, document_id=doc1_inv.id, field_group="valuation",
            field_key="invoice_grand_total", field_label="Invoice Grand Total",
            field_value="142500.00", raw_value="$142,500.00 USD",
            confidence_score=99.0, is_low_confidence=False, is_confirmed=True,
            bounding_box={"page": 1, "x": 560, "y": 580, "w": 180, "h": 28}
        ),
        # Packing list fields
        ExtractedField(
            shipment_id=shp1.id, document_id=doc1_pl.id, field_group="packages",
            field_key="pl_package_count", field_label="Total Packages / Pallets",
            field_value="42 Pallets (840 Cartons)", raw_value="42 PALLETS / 840 CTNS",
            confidence_score=96.5, is_low_confidence=False, is_confirmed=True,
            bounding_box={"page": 1, "x": 60, "y": 280, "w": 240, "h": 25}
        ),
        ExtractedField(
            shipment_id=shp1.id, document_id=doc1_pl.id, field_group="packages",
            field_key="pl_container_number", field_label="Container Number",
            field_value="MSKU9281745", raw_value="MSKU 928174-5",
            confidence_score=97.5, is_low_confidence=False, is_confirmed=True,
            bounding_box={"page": 1, "x": 380, "y": 280, "w": 180, "h": 25}
        ),
        # LOW CONFIDENCE FIELD (<85%) -> Amber Highlight
        ExtractedField(
            shipment_id=shp1.id, document_id=doc1_pl.id, field_group="packages",
            field_key="pl_seal_number", field_label="Carrier Seal Number",
            field_value="SL-839201", raw_value="SL-839201",
            confidence_score=79.4, is_low_confidence=True, is_confirmed=False,
            bounding_box={"page": 1, "x": 580, "y": 280, "w": 150, "h": 25}
        ),
        ExtractedField(
            shipment_id=shp1.id, document_id=doc1_pl.id, field_group="weights",
            field_key="packing_list_gross_weight", field_label="Packing List Gross Weight (kg)",
            field_value="12450.00", raw_value="12,450.00 KGS",
            confidence_score=98.5, is_low_confidence=False, is_confirmed=True,
            bounding_box={"page": 1, "x": 420, "y": 480, "w": 170, "h": 26}
        ),
        ExtractedField(
            shipment_id=shp1.id, document_id=doc1_pl.id, field_group="weights",
            field_key="packing_list_net_weight", field_label="Packing List Net Weight (kg)",
            field_value="11200.00", raw_value="11,200.00 KGS",
            confidence_score=97.1, is_low_confidence=False, is_confirmed=True,
            bounding_box={"page": 1, "x": 420, "y": 510, "w": 170, "h": 26}
        ),
        # Bill of Lading fields
        ExtractedField(
            shipment_id=shp1.id, document_id=doc1_bl.id, field_group="metadata",
            field_key="bl_number", field_label="Bill of Lading Number",
            field_value="MAEU92837190", raw_value="MAEU-92837190",
            confidence_score=99.1, is_low_confidence=False, is_confirmed=True,
            bounding_box={"page": 1, "x": 520, "y": 60, "w": 190, "h": 24}
        ),
        ExtractedField(
            shipment_id=shp1.id, document_id=doc1_bl.id, field_group="parties",
            field_key="bl_consignee_name", field_label="Consignee on BL",
            field_value="Apex Logistics Global LLC", raw_value="Apex Logistics Global LLC",
            confidence_score=98.0, is_low_confidence=False, is_confirmed=True,
            bounding_box={"page": 1, "x": 60, "y": 160, "w": 300, "h": 32}
        ),
        ExtractedField(
            shipment_id=shp1.id, document_id=doc1_bl.id, field_group="metadata",
            field_key="bl_port_of_discharge", field_label="Port of Discharge on BL",
            field_value="Port of Los Angeles, US", raw_value="PORT OF LOS ANGELES, USA",
            confidence_score=97.3, is_low_confidence=False, is_confirmed=True,
            bounding_box={"page": 1, "x": 380, "y": 240, "w": 220, "h": 22}
        ),
        ExtractedField(
            shipment_id=shp1.id, document_id=doc1_bl.id, field_group="packages",
            field_key="bl_container_number", field_label="BL Container Number",
            field_value="MSKU9281745", raw_value="MSKU9281745",
            confidence_score=98.3, is_low_confidence=False, is_confirmed=True,
            bounding_box={"page": 1, "x": 60, "y": 340, "w": 180, "h": 24}
        ),
        ExtractedField(
            shipment_id=shp1.id, document_id=doc1_bl.id, field_group="packages",
            field_key="bl_seal_number", field_label="Carrier Seal Number on BL",
            field_value="SL-839201", raw_value="SL-839201",
            confidence_score=96.8, is_low_confidence=False, is_confirmed=True,
            bounding_box={"page": 1, "x": 260, "y": 340, "w": 150, "h": 24}
        ),
        # CRITICAL DISCREPANCY FIELD: BL gross weight is 12,800.00 kg vs 12,450.00 kg (+350 kg)
        ExtractedField(
            shipment_id=shp1.id, document_id=doc1_bl.id, field_group="weights",
            field_key="bl_gross_weight", field_label="BL Gross Weight (kg)",
            field_value="12800.00", raw_value="12,800.00 KGS",
            confidence_score=98.9, is_low_confidence=False, is_confirmed=True,
            bounding_box={"page": 1, "x": 500, "y": 340, "w": 170, "h": 26}
        ),
    ]
    db.add_all(fields_shp1)

    # Line items for Shipment 1
    items_shp1 = [
        LineItem(
            shipment_id=shp1.id, item_number=1,
            description="High Performance ARM Cortex Microcontrollers (SMD-64)",
            hsn_code="8542.31.00", quantity=10000.0, unit="PCS",
            unit_price=4.50, total_amount=45000.00, currency="USD",
            confidence_score=78.2, # Low confidence (<85%)
            is_confirmed=False
        ),
        LineItem(
            shipment_id=shp1.id, item_number=2,
            description="Multi-layer PCB Rigid-Flex Board Assemblies",
            hsn_code="8534.00.00", quantity=5000.0, unit="PCS",
            unit_price=12.20, total_amount=61000.00, currency="USD",
            confidence_score=96.4, is_confirmed=True
        ),
        LineItem(
            shipment_id=shp1.id, item_number=3,
            description="High Speed NVMe Storage Flash Controller ICs",
            hsn_code="8542.32.00", quantity=2500.0, unit="PCS",
            unit_price=14.60, total_amount=36500.00, currency="USD",
            confidence_score=94.1, is_confirmed=True
        )
    ]
    db.add_all(items_shp1)
    db.flush()

    # Initial Cross-Check Execution for Shipment 1
    checks_shp1 = CrossCheckEngine.run_all_validations(shp1)
    for c in checks_shp1:
        db.add(c)

    # Audit log
    db.add(AuditLog(
        shipment_id=shp1.id,
        user_role="System / Vision AI",
        user_name="VisionExtractor-v4.2",
        action="EXTRACTION_COMPLETED",
        details="Extracted 18 fields and 3 line items across Commercial Invoice, Packing List, and Bill of Lading. Flagged 2 low-confidence fields (<85%).",
        timestamp=shp1.created_at + datetime.timedelta(minutes=2)
    ))
    db.add(AuditLog(
        shipment_id=shp1.id,
        user_role="System / CrossCheck Engine",
        user_name="RuleEngine-Deterministic",
        action="CROSS_CHECK_FAILED",
        details="RULE_GROSS_WEIGHT_CONSISTENCY failed: Discrepancy of +350.0 kg (+2.81%) detected between BL (12,800.0 kg) and Invoice/PL (12,450.0 kg). Export blocked.",
        timestamp=shp1.created_at + datetime.timedelta(minutes=3)
    ))

    # =========================================================================
    # SHIPMENT 2: Nordic CleanTech AB (Pending Review)
    # =========================================================================
    shp2 = Shipment(
        shipment_number="SHP-2026-9015",
        supplier_name="Nordic CleanTech AB",
        supplier_country="Sweden",
        consignee_name="PureWater Solutions Inc.",
        consignee_country="United States",
        port_of_loading="Gothenburg, SE",
        port_of_discharge="Port of Newark, NJ, US",
        vessel_name="ATLANTIC CONVEYOR",
        voyage_number="2026-E44",
        status="Pending Review",
        total_declared_value=89400.00,
        currency="USD",
        notes="Industrial water treatment membrane modules. Pending Executive review of low-confidence seal field.",
        created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=14),
        updated_at=datetime.datetime.utcnow() - datetime.timedelta(hours=2)
    )
    db.add(shp2)
    db.flush()

    doc2_inv = Document(
        shipment_id=shp2.id, doc_type="commercial_invoice",
        file_name="NORDIC_CLEANTECH_INVOICE_SE-991.pdf",
        file_path="uploads/NORDIC_CLEANTECH_INVOICE_SE-991.pdf",
        file_size=210400, page_count=1, uploaded_at=shp2.created_at
    )
    doc2_pl = Document(
        shipment_id=shp2.id, doc_type="packing_list",
        file_name="NORDIC_CLEANTECH_PACKING_LIST.pdf",
        file_path="uploads/NORDIC_CLEANTECH_PACKING_LIST.pdf",
        file_size=175600, page_count=1, uploaded_at=shp2.created_at
    )
    doc2_bl = Document(
        shipment_id=shp2.id, doc_type="bill_of_lading",
        file_name="OCEAN_BL_ACL-7749102.pdf",
        file_path="uploads/OCEAN_BL_ACL-7749102.pdf",
        file_size=298000, page_count=1, uploaded_at=shp2.created_at
    )
    db.add_all([doc2_inv, doc2_pl, doc2_bl])
    db.flush()

    fields_shp2 = [
        ExtractedField(shipment_id=shp2.id, document_id=doc2_inv.id, field_group="metadata", field_key="invoice_number", field_label="Invoice Number", field_value="NC-2026-SE-991", confidence_score=99.0, is_confirmed=True),
        ExtractedField(shipment_id=shp2.id, document_id=doc2_inv.id, field_group="valuation", field_key="invoice_grand_total", field_label="Invoice Grand Total", field_value="89400.00", confidence_score=98.5, is_confirmed=True),
        ExtractedField(shipment_id=shp2.id, document_id=doc2_inv.id, field_group="weights", field_key="invoice_gross_weight", field_label="Invoice Gross Weight (kg)", field_value="4820.00", confidence_score=97.0, is_confirmed=True),
        ExtractedField(shipment_id=shp2.id, document_id=doc2_pl.id, field_group="weights", field_key="packing_list_gross_weight", field_label="Packing List Gross Weight (kg)", field_value="4820.00", confidence_score=98.0, is_confirmed=True),
        ExtractedField(shipment_id=shp2.id, document_id=doc2_bl.id, field_group="weights", field_key="bl_gross_weight", field_label="BL Gross Weight (kg)", field_value="4820.00", confidence_score=98.5, is_confirmed=True),
        ExtractedField(shipment_id=shp2.id, document_id=doc2_bl.id, field_group="metadata", field_key="bl_number", field_label="Bill of Lading Number", field_value="ACL-7749102", confidence_score=99.0, is_confirmed=True),
        ExtractedField(shipment_id=shp2.id, document_id=doc2_pl.id, field_group="packages", field_key="pl_container_number", field_label="Container Number", field_value="ACLU8492011", confidence_score=96.0, is_confirmed=True),
        ExtractedField(shipment_id=shp2.id, document_id=doc2_bl.id, field_group="packages", field_key="bl_container_number", field_label="BL Container Number", field_value="ACLU8492011", confidence_score=97.0, is_confirmed=True),
        # Low confidence seal number
        ExtractedField(shipment_id=shp2.id, document_id=doc2_pl.id, field_group="packages", field_key="pl_seal_number", field_label="Carrier Seal Number", field_value="SE-99410", raw_value="SE-99410", confidence_score=81.2, is_low_confidence=True, is_confirmed=False),
    ]
    db.add_all(fields_shp2)

    items_shp2 = [
        LineItem(shipment_id=shp2.id, item_number=1, description="Ceramic Ultrafiltration Membrane Modules (Grade-X)", hsn_code="8421.21.00", quantity=400.0, unit="PCS", unit_price=145.00, total_amount=58000.00, currency="USD", confidence_score=98.0, is_confirmed=True),
        LineItem(shipment_id=shp2.id, item_number=2, description="High-Pressure Reverse Osmosis Membrane Housings", hsn_code="8421.99.00", quantity=80.0, unit="PCS", unit_price=392.50, total_amount=31400.00, currency="USD", confidence_score=96.5, is_confirmed=True),
    ]
    db.add_all(items_shp2)
    db.flush()

    for c in CrossCheckEngine.run_all_validations(shp2):
        db.add(c)

    db.add(AuditLog(
        shipment_id=shp2.id,
        user_role="System / Vision AI",
        user_name="VisionExtractor-v4.2",
        action="EXTRACTION_COMPLETED",
        details="Extraction completed successfully. 1 low-confidence field flagged for Executive review.",
        timestamp=shp2.created_at + datetime.timedelta(minutes=1)
    ))

    # =========================================================================
    # SHIPMENT 3: Kyoto Robotics Industrial Corp (Cleared / Approved)
    # =========================================================================
    shp3 = Shipment(
        shipment_number="SHP-2026-7831",
        supplier_name="Kyoto Robotics Industrial Corp",
        supplier_country="Japan",
        consignee_name="Cobot Automation North America Corp",
        consignee_country="United States",
        port_of_loading="Kobe, JP",
        port_of_discharge="Port of Long Beach, CA, US",
        vessel_name="ONE APUS",
        voyage_number="0081E",
        status="Cleared",
        total_declared_value=318500.00,
        currency="USD",
        notes="High precision 6-axis robotic arms. All documents reconciled, weights matched, manager sign-off complete.",
        created_at=datetime.datetime.utcnow() - datetime.timedelta(days=1, hours=4),
        updated_at=datetime.datetime.utcnow() - datetime.timedelta(hours=3)
    )
    db.add(shp3)
    db.flush()

    doc3_inv = Document(shipment_id=shp3.id, doc_type="commercial_invoice", file_name="KYOTO_ROBOTICS_INV-2026-04.pdf", file_path="uploads/KYOTO_ROBOTICS_INV-2026-04.pdf", file_size=280000, page_count=2, uploaded_at=shp3.created_at)
    doc3_pl = Document(shipment_id=shp3.id, doc_type="packing_list", file_name="KYOTO_ROBOTICS_PL-2026-04.pdf", file_path="uploads/KYOTO_ROBOTICS_PL-2026-04.pdf", file_size=190000, page_count=2, uploaded_at=shp3.created_at)
    doc3_bl = Document(shipment_id=shp3.id, doc_type="bill_of_lading", file_name="ONE_BL_ONEY772810.pdf", file_path="uploads/ONE_BL_ONEY772810.pdf", file_size=325000, page_count=1, uploaded_at=shp3.created_at)
    db.add_all([doc3_inv, doc3_pl, doc3_bl])
    db.flush()

    fields_shp3 = [
        ExtractedField(shipment_id=shp3.id, document_id=doc3_inv.id, field_group="metadata", field_key="invoice_number", field_label="Invoice Number", field_value="KR-2026-04", confidence_score=99.5, is_confirmed=True),
        ExtractedField(shipment_id=shp3.id, document_id=doc3_inv.id, field_group="valuation", field_key="invoice_grand_total", field_label="Invoice Grand Total", field_value="318500.00", confidence_score=99.4, is_confirmed=True),
        ExtractedField(shipment_id=shp3.id, document_id=doc3_inv.id, field_group="weights", field_key="invoice_gross_weight", field_label="Invoice Gross Weight (kg)", field_value="18400.00", confidence_score=99.0, is_confirmed=True),
        ExtractedField(shipment_id=shp3.id, document_id=doc3_pl.id, field_group="weights", field_key="packing_list_gross_weight", field_label="Packing List Gross Weight (kg)", field_value="18400.00", confidence_score=99.0, is_confirmed=True),
        ExtractedField(shipment_id=shp3.id, document_id=doc3_bl.id, field_group="weights", field_key="bl_gross_weight", field_label="BL Gross Weight (kg)", field_value="18400.00", confidence_score=99.2, is_confirmed=True),
        ExtractedField(shipment_id=shp3.id, document_id=doc3_bl.id, field_group="metadata", field_key="bl_number", field_label="Bill of Lading Number", field_value="ONEY772810", confidence_score=99.8, is_confirmed=True),
        ExtractedField(shipment_id=shp3.id, document_id=doc3_pl.id, field_group="packages", field_key="pl_container_number", field_label="Container Number", field_value="TGHU9931820", confidence_score=98.5, is_confirmed=True),
        ExtractedField(shipment_id=shp3.id, document_id=doc3_bl.id, field_group="packages", field_key="bl_container_number", field_label="BL Container Number", field_value="TGHU9931820", confidence_score=98.9, is_confirmed=True),
    ]
    db.add_all(fields_shp3)

    items_shp3 = [
        LineItem(shipment_id=shp3.id, item_number=1, description="Industrial 6-Axis Articulated Robot Arm Assemblies (KR-500)", hsn_code="8479.50.00", quantity=10.0, unit="UNITS", unit_price=24500.00, total_amount=245000.00, currency="USD", confidence_score=99.0, is_confirmed=True),
        LineItem(shipment_id=shp3.id, item_number=2, description="Teach Pendant Controllers and Safety Drive Units", hsn_code="8537.10.90", quantity=10.0, unit="UNITS", unit_price=7350.00, total_amount=73500.00, currency="USD", confidence_score=98.5, is_confirmed=True),
    ]
    db.add_all(items_shp3)
    db.flush()

    for c in CrossCheckEngine.run_all_validations(shp3):
        c.status = "PASSED"
        c.is_blocking = False
        db.add(c)

    db.add(AuditLog(
        shipment_id=shp3.id,
        user_role="Documentation Manager",
        user_name="Sarah Chen",
        action="SHIPMENT_CLEARED",
        details="All 5 deterministic cross-check validations passed. High-confidence extraction. Customs clearance approved.",
        timestamp=shp3.updated_at
    ))

    # =========================================================================
    # SHIPMENT 4: Bavaria Auto Components GmbH (Party Discrepancy)
    # =========================================================================
    shp4 = Shipment(
        shipment_number="SHP-2026-9140",
        supplier_name="Bavaria Auto Components GmbH",
        supplier_country="Germany",
        consignee_name="Detroit EV Systems Inc.",
        consignee_country="United States",
        port_of_loading="Hamburg, DE",
        port_of_discharge="Detroit Intermodal Terminal, MI, US",
        vessel_name="MSC ISABELLA",
        voyage_number="EU-US-09",
        status="Cross-Check Failed",
        total_declared_value=176000.00,
        currency="USD",
        notes="Automotive braking units. Consignee entity discrepancy between BL and Invoice.",
        created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=22),
        updated_at=datetime.datetime.utcnow() - datetime.timedelta(hours=5)
    )
    db.add(shp4)
    db.flush()

    doc4_inv = Document(shipment_id=shp4.id, doc_type="commercial_invoice", file_name="BAVARIA_AUTO_INV-8910.pdf", file_path="uploads/BAVARIA_AUTO_INV-8910.pdf", file_size=230000, page_count=1, uploaded_at=shp4.created_at)
    doc4_pl = Document(shipment_id=shp4.id, doc_type="packing_list", file_name="BAVARIA_AUTO_PL-8910.pdf", file_path="uploads/BAVARIA_AUTO_PL-8910.pdf", file_size=180000, page_count=1, uploaded_at=shp4.created_at)
    doc4_bl = Document(shipment_id=shp4.id, doc_type="bill_of_lading", file_name="MSC_BL_MSCU817290.pdf", file_path="uploads/MSC_BL_MSCU817290.pdf", file_size=310000, page_count=1, uploaded_at=shp4.created_at)
    db.add_all([doc4_inv, doc4_pl, doc4_bl])
    db.flush()

    fields_shp4 = [
        ExtractedField(shipment_id=shp4.id, document_id=doc4_inv.id, field_group="parties", field_key="invoice_consignee_name", field_label="Invoice Consignee", field_value="Detroit EV Systems Inc.", confidence_score=98.0, is_confirmed=True),
        # Discrepant consignee on BL
        ExtractedField(shipment_id=shp4.id, document_id=doc4_bl.id, field_group="parties", field_key="bl_consignee_name", field_label="BL Consignee", field_value="Vanguard Logistics Services LLC (Unmatched)", confidence_score=97.0, is_confirmed=True),
        ExtractedField(shipment_id=shp4.id, document_id=doc4_inv.id, field_group="valuation", field_key="invoice_grand_total", field_label="Invoice Grand Total", field_value="176000.00", confidence_score=99.0, is_confirmed=True),
        ExtractedField(shipment_id=shp4.id, document_id=doc4_inv.id, field_group="weights", field_key="invoice_gross_weight", field_label="Invoice Gross Weight (kg)", field_value="9100.00", confidence_score=98.0, is_confirmed=True),
        ExtractedField(shipment_id=shp4.id, document_id=doc4_pl.id, field_group="weights", field_key="packing_list_gross_weight", field_label="Packing List Gross Weight (kg)", field_value="9100.00", confidence_score=98.0, is_confirmed=True),
        ExtractedField(shipment_id=shp4.id, document_id=doc4_bl.id, field_group="weights", field_key="bl_gross_weight", field_label="BL Gross Weight (kg)", field_value="9100.00", confidence_score=98.5, is_confirmed=True),
    ]
    db.add_all(fields_shp4)

    items_shp4 = [
        LineItem(shipment_id=shp4.id, item_number=1, description="Electronic Regenerative Braking Calipers (Dual Piston)", hsn_code="8708.30.00", quantity=2000.0, unit="PCS", unit_price=88.00, total_amount=176000.00, currency="USD", confidence_score=97.0, is_confirmed=True),
    ]
    db.add_all(items_shp4)
    db.flush()

    for c in CrossCheckEngine.run_all_validations(shp4):
        db.add(c)

    db.add(AuditLog(
        shipment_id=shp4.id,
        user_role="System / CrossCheck Engine",
        user_name="RuleEngine-Deterministic",
        action="CROSS_CHECK_FAILED",
        details="RULE_CONSIGNEE_PORT_MATCH failed: Consignee on BL ('Vanguard Logistics Services LLC') does not match Invoice Consignee ('Detroit EV Systems Inc.').",
        timestamp=shp4.created_at + datetime.timedelta(minutes=2)
    ))

    db.commit()
    print("Database seeding completed successfully!")

