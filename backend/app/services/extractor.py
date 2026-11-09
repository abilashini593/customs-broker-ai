import datetime
import random
from typing import List, Dict, Any, Tuple
from app.models.shipment import Document, ExtractedField, LineItem

class VisionExtractorService:
    """
    Vision AI Ingestion & Layout Parsing Service.
    Simulates high-precision OCR & Vision Model extraction with document
    bounding boxes, entity tagging, and confidence metrics.
    """

    @classmethod
    def extract_document(cls, shipment_id: int, document: Document) -> Tuple[List[ExtractedField], List[LineItem]]:
        """
        Parses document according to doc_type and extracts structured fields and line items.
        """
        doc_type = document.doc_type
        file_name = document.file_name or ""
        fields: List[ExtractedField] = []
        line_items: List[LineItem] = []

        if doc_type == "commercial_invoice":
            fields, line_items = cls._extract_invoice(shipment_id, document.id, file_name)
        elif doc_type == "packing_list":
            fields = cls._extract_packing_list(shipment_id, document.id, file_name)
        elif doc_type == "bill_of_lading":
            fields = cls._extract_bill_of_lading(shipment_id, document.id, file_name)
        else:
            fields = cls._extract_generic(shipment_id, document.id)

        return fields, line_items

    @classmethod
    def _extract_invoice(cls, shipment_id: int, doc_id: int, file_name: str = "") -> Tuple[List[ExtractedField], List[LineItem]]:
        if "9999" in file_name or "TEST" in file_name:
            fields = [
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="metadata",
                    field_key="invoice_number",
                    field_label="Invoice Number",
                    field_value="INV-9999",
                    raw_value="INV-9999",
                    confidence_score=99.9,
                    is_low_confidence=False,
                    is_confirmed=True,
                    confirmed_by="Auto-Verified",
                    bounding_box={"page": 1, "x": 72, "y": 140, "w": 180, "h": 22}
                ),
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="metadata",
                    field_key="invoice_date",
                    field_label="Invoice Date",
                    field_value="2026-11-09",
                    raw_value="09/11/2026",
                    confidence_score=98.5,
                    is_low_confidence=False,
                    is_confirmed=True,
                    confirmed_by="Auto-Verified",
                    bounding_box={"page": 1, "x": 72, "y": 168, "w": 140, "h": 20}
                ),
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="parties",
                    field_key="invoice_supplier_name",
                    field_label="Exporter / Shipper",
                    field_value="Tokyo Semiconductor Systems Corp",
                    raw_value="Tokyo Semiconductor Systems Corp",
                    confidence_score=99.0,
                    is_low_confidence=False,
                    is_confirmed=True,
                    confirmed_by="Auto-Verified",
                    bounding_box={"page": 1, "x": 72, "y": 80, "w": 310, "h": 28}
                ),
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="parties",
                    field_key="invoice_consignee_name",
                    field_label="Consignee / Importer",
                    field_value="Pacific Crest Electronics LLC",
                    raw_value="Pacific Crest Electronics LLC",
                    confidence_score=98.8,
                    is_low_confidence=False,
                    is_confirmed=True,
                    confirmed_by="Auto-Verified",
                    bounding_box={"page": 1, "x": 420, "y": 80, "w": 280, "h": 28}
                ),
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="metadata",
                    field_key="invoice_port_of_discharge",
                    field_label="Port of Discharge",
                    field_value="Port of Long Beach, US",
                    raw_value="Long Beach Harbor, CA",
                    confidence_score=97.5,
                    is_low_confidence=False,
                    is_confirmed=True,
                    confirmed_by="Auto-Verified",
                    bounding_box={"page": 1, "x": 420, "y": 195, "w": 220, "h": 22}
                ),
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="packages",
                    field_key="container_number",
                    field_label="Container Number",
                    field_value="MSKU-999910",
                    raw_value="MSKU-999910",
                    confidence_score=98.5,
                    is_low_confidence=False,
                    is_confirmed=True
                ),
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="packages",
                    field_key="seal_number",
                    field_label="Carrier Seal Number",
                    field_value="SL-999901",
                    raw_value="SL-999901",
                    confidence_score=97.0,
                    is_low_confidence=False,
                    is_confirmed=True
                ),
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="weights",
                    field_key="invoice_gross_weight",
                    field_label="Invoice Gross Weight (kg)",
                    field_value="15000.00",
                    raw_value="15,000.00 KGS",
                    confidence_score=98.2,
                    is_low_confidence=False,
                    is_confirmed=True,
                    confirmed_by="Auto-Verified",
                    bounding_box={"page": 1, "x": 420, "y": 510, "w": 160, "h": 24}
                ),
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="valuation",
                    field_key="invoice_grand_total",
                    field_label="Invoice Grand Total",
                    field_value="400000.00",
                    raw_value="$400,000.00 USD",
                    confidence_score=99.8,
                    is_low_confidence=False,
                    is_confirmed=True,
                    confirmed_by="Auto-Verified",
                    bounding_box={"page": 1, "x": 560, "y": 580, "w": 180, "h": 28}
                ),
            ]
            line_items = [
                LineItem(
                    shipment_id=shipment_id,
                    item_number=1,
                    description="Enterprise AI Accelerator Chips (H100-SXM5)",
                    hsn_code="8542.31.00",
                    quantity=200.0,
                    unit="PCS",
                    unit_price=1500.00,
                    total_amount=300000.00,
                    currency="USD",
                    confidence_score=98.5,
                    is_confirmed=True
                ),
                LineItem(
                    shipment_id=shipment_id,
                    item_number=2,
                    description="High-Density ECC Server RAM Modules (128GB)",
                    hsn_code="8473.30.00",
                    quantity=500.0,
                    unit="PCS",
                    unit_price=200.00,
                    total_amount=100000.00,
                    currency="USD",
                    confidence_score=97.0,
                    is_confirmed=True
                )
            ]
            return fields, line_items

        # Default fallback items
        fields = [
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="metadata",
                field_key="invoice_number",
                field_label="Invoice Number",
                field_value="INV-2026-CN-8841",
                raw_value="INV-2026-CN-8841",
                confidence_score=99.2,
                is_low_confidence=False,
                is_confirmed=True,
                confirmed_by="Auto-Verified",
                bounding_box={"page": 1, "x": 72, "y": 140, "w": 180, "h": 22}
            ),
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="metadata",
                field_key="invoice_date",
                field_label="Invoice Date",
                field_value="2026-10-18",
                raw_value="18/10/2026",
                confidence_score=94.5,
                is_low_confidence=False,
                is_confirmed=True,
                confirmed_by="Auto-Verified",
                bounding_box={"page": 1, "x": 72, "y": 168, "w": 140, "h": 20}
            ),
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="parties",
                field_key="invoice_supplier_name",
                field_label="Exporter / Shipper",
                field_value="Shenzhen Precision Microelectronics Co., Ltd.",
                raw_value="Shenzhen Precision Microelectronics Co., Ltd.",
                confidence_score=98.8,
                is_low_confidence=False,
                is_confirmed=True,
                confirmed_by="Auto-Verified",
                bounding_box={"page": 1, "x": 72, "y": 80, "w": 310, "h": 28}
            ),
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="parties",
                field_key="invoice_consignee_name",
                field_label="Consignee / Importer",
                field_value="Apex Logistics Global LLC",
                raw_value="Apex Logistics Global LLC",
                confidence_score=97.1,
                is_low_confidence=False,
                is_confirmed=True,
                confirmed_by="Auto-Verified",
                bounding_box={"page": 1, "x": 420, "y": 80, "w": 280, "h": 28}
            ),
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="metadata",
                field_key="invoice_port_of_discharge",
                field_label="Port of Discharge",
                field_value="Port of Los Angeles, US",
                raw_value="Los Angeles Harbor, CA",
                confidence_score=96.3,
                is_low_confidence=False,
                is_confirmed=True,
                confirmed_by="Auto-Verified",
                bounding_box={"page": 1, "x": 420, "y": 195, "w": 220, "h": 22}
            ),
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="packages",
                field_key="container_number",
                field_label="Container Number",
                field_value="MSKU9281745",
                raw_value="MSKU 928174-5",
                confidence_score=97.5,
                is_low_confidence=False,
                is_confirmed=True
            ),
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="packages",
                field_key="seal_number",
                field_label="Seal Number",
                field_value="SL-839201",
                raw_value="SL-839201",
                confidence_score=81.4,
                is_low_confidence=True,
                is_confirmed=False
            ),
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="weights",
                field_key="invoice_gross_weight",
                field_label="Invoice Gross Weight (kg)",
                field_value="12450.00",
                raw_value="12,450.00 KGS",
                confidence_score=97.4,
                is_low_confidence=False,
                is_confirmed=True,
                confirmed_by="Auto-Verified",
                bounding_box={"page": 1, "x": 420, "y": 510, "w": 160, "h": 24}
            ),
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="valuation",
                field_key="invoice_grand_total",
                field_label="Invoice Grand Total",
                field_value="142500.00",
                raw_value="$142,500.00 USD",
                confidence_score=99.0,
                is_low_confidence=False,
                is_confirmed=True,
                confirmed_by="Auto-Verified",
                bounding_box={"page": 1, "x": 560, "y": 580, "w": 180, "h": 28}
            ),
        ]

        line_items = [
            LineItem(
                shipment_id=shipment_id,
                item_number=1,
                description="High Performance ARM Cortex Microcontrollers (SMD-64)",
                hsn_code="8542.31.00",
                quantity=10000.0,
                unit="PCS",
                unit_price=4.50,
                total_amount=45000.00,
                currency="USD",
                confidence_score=78.2,
                is_confirmed=False
            ),
            LineItem(
                shipment_id=shipment_id,
                item_number=2,
                description="Multi-layer PCB Rigid-Flex Board Assemblies",
                hsn_code="8534.00.00",
                quantity=5000.0,
                unit="PCS",
                unit_price=12.20,
                total_amount=61000.00,
                currency="USD",
                confidence_score=96.4,
                is_confirmed=True
            ),
            LineItem(
                shipment_id=shipment_id,
                item_number=3,
                description="High Speed NVMe Storage Flash Controller ICs",
                hsn_code="8542.32.00",
                quantity=2500.0,
                unit="PCS",
                unit_price=14.60,
                total_amount=36500.00,
                currency="USD",
                confidence_score=94.1,
                is_confirmed=True
            )
        ]

        return fields, line_items

    @classmethod
    def _extract_packing_list(cls, shipment_id: int, doc_id: int, file_name: str = "") -> List[ExtractedField]:
        if "9999" in file_name or "TEST" in file_name:
            return [
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="metadata",
                    field_key="packing_list_number",
                    field_label="Packing List Number",
                    field_value="PL-9999",
                    raw_value="PL-9999",
                    confidence_score=98.9,
                    is_low_confidence=False,
                    is_confirmed=True,
                    confirmed_by="Auto-Verified",
                    bounding_box={"page": 1, "x": 60, "y": 130, "w": 180, "h": 22}
                ),
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="parties",
                    field_key="pl_consignee_name",
                    field_label="Consignee",
                    field_value="Pacific Crest Electronics LLC",
                    raw_value="Pacific Crest Electronics LLC",
                    confidence_score=98.5,
                    is_low_confidence=False,
                    is_confirmed=True,
                    bounding_box={"page": 1, "x": 60, "y": 180, "w": 240, "h": 25}
                ),
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="packages",
                    field_key="pl_package_count",
                    field_label="Total Packages / Pallets",
                    field_value="25 Pallets (500 Cartons)",
                    raw_value="25 PALLETS / 500 CTNS",
                    confidence_score=97.2,
                    is_low_confidence=False,
                    is_confirmed=True,
                    bounding_box={"page": 1, "x": 60, "y": 280, "w": 240, "h": 25}
                ),
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="packages",
                    field_key="container_number",
                    field_label="Container Number",
                    field_value="MSKU-999910",
                    raw_value="MSKU-999910",
                    confidence_score=98.5,
                    is_low_confidence=False,
                    is_confirmed=True,
                    bounding_box={"page": 1, "x": 380, "y": 280, "w": 180, "h": 25}
                ),
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="packages",
                    field_key="seal_number",
                    field_label="Seal Number",
                    field_value="SL-999901",
                    raw_value="SL-999901",
                    confidence_score=97.0,
                    is_low_confidence=False,
                    is_confirmed=True,
                    bounding_box={"page": 1, "x": 580, "y": 280, "w": 150, "h": 25}
                ),
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="weights",
                    field_key="packing_list_gross_weight",
                    field_label="Packing List Gross Weight (kg)",
                    field_value="15000.00",
                    raw_value="15,000.00 KGS",
                    confidence_score=98.5,
                    is_low_confidence=False,
                    is_confirmed=True,
                    bounding_box={"page": 1, "x": 420, "y": 480, "w": 170, "h": 26}
                ),
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="weights",
                    field_key="packing_list_net_weight",
                    field_label="Packing List Net Weight (kg)",
                    field_value="13500.00",
                    raw_value="13,500.00 KGS",
                    confidence_score=97.1,
                    is_low_confidence=False,
                    is_confirmed=True,
                    bounding_box={"page": 1, "x": 420, "y": 510, "w": 170, "h": 26}
                ),
            ]

        return [
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="metadata",
                field_key="packing_list_number",
                field_label="Packing List Number",
                field_value="PL-2026-CN-8841",
                raw_value="PL-2026-CN-8841",
                confidence_score=98.9,
                is_low_confidence=False,
                is_confirmed=True,
                confirmed_by="Auto-Verified",
                bounding_box={"page": 1, "x": 60, "y": 130, "w": 180, "h": 22}
            ),
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="packages",
                field_key="pl_package_count",
                field_label="Total Packages / Pallets",
                field_value="42 Pallets (840 Cartons)",
                raw_value="42 PALLETS / 840 CTNS",
                confidence_score=96.2,
                is_low_confidence=False,
                is_confirmed=True,
                bounding_box={"page": 1, "x": 60, "y": 280, "w": 240, "h": 25}
            ),
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="packages",
                field_key="container_number",
                field_label="Container Number",
                field_value="MSKU9281745",
                raw_value="MSKU 928174-5",
                confidence_score=97.5,
                is_low_confidence=False,
                is_confirmed=True,
                bounding_box={"page": 1, "x": 380, "y": 280, "w": 180, "h": 25}
            ),
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="packages",
                field_key="seal_number",
                field_label="Seal Number",
                field_value="SL-839201",
                raw_value="SL-839201",
                confidence_score=81.4,
                is_low_confidence=True,
                is_confirmed=False,
                bounding_box={"page": 1, "x": 580, "y": 280, "w": 150, "h": 25}
            ),
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="weights",
                field_key="packing_list_gross_weight",
                field_label="Packing List Gross Weight (kg)",
                field_value="12450.00",
                raw_value="12,450.00 KGS",
                confidence_score=98.5,
                is_low_confidence=False,
                is_confirmed=True,
                bounding_box={"page": 1, "x": 420, "y": 480, "w": 170, "h": 26}
            ),
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="weights",
                field_key="packing_list_net_weight",
                field_label="Packing List Net Weight (kg)",
                field_value="11200.00",
                raw_value="11,200.00 KGS",
                confidence_score=97.1,
                is_low_confidence=False,
                is_confirmed=True,
                bounding_box={"page": 1, "x": 420, "y": 510, "w": 170, "h": 26}
            ),
        ]

    @classmethod
    def _extract_bill_of_lading(cls, shipment_id: int, doc_id: int, file_name: str = "") -> List[ExtractedField]:
        if "9999" in file_name or "TEST" in file_name:
            return [
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="metadata",
                    field_key="bl_number",
                    field_label="Bill of Lading Number",
                    field_value="MAEU-9999-REV",
                    raw_value="MAEU-9999-REV",
                    confidence_score=99.1,
                    is_low_confidence=False,
                    is_confirmed=True,
                    bounding_box={"page": 1, "x": 520, "y": 60, "w": 190, "h": 24}
                ),
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="parties",
                    field_key="bl_shipper_name",
                    field_label="Shipper / Exporter",
                    field_value="Tokyo Semiconductor Systems Corp",
                    raw_value="Tokyo Semiconductor Systems Corp",
                    confidence_score=99.0,
                    is_low_confidence=False,
                    is_confirmed=True,
                    bounding_box={"page": 1, "x": 60, "y": 100, "w": 300, "h": 32}
                ),
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="parties",
                    field_key="bl_consignee_name",
                    field_label="Consignee",
                    field_value="Pacific Crest Electronics LLC",
                    raw_value="Pacific Crest Electronics LLC",
                    confidence_score=98.8,
                    is_low_confidence=False,
                    is_confirmed=True,
                    bounding_box={"page": 1, "x": 60, "y": 160, "w": 300, "h": 32}
                ),
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="metadata",
                    field_key="bl_vessel_voyage",
                    field_label="Ocean Vessel / Voyage",
                    field_value="EVER GIVEN / 0428-091W",
                    raw_value="EVER GIVEN V. 0428-091W",
                    confidence_score=96.7,
                    is_low_confidence=False,
                    is_confirmed=True,
                    bounding_box={"page": 1, "x": 60, "y": 240, "w": 250, "h": 22}
                ),
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="metadata",
                    field_key="bl_port_of_discharge",
                    field_label="Port of Discharge",
                    field_value="Port of Long Beach, US",
                    raw_value="Port of Long Beach, US",
                    confidence_score=98.0,
                    is_low_confidence=False,
                    is_confirmed=True,
                    bounding_box={"page": 1, "x": 380, "y": 240, "w": 220, "h": 22}
                ),
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="packages",
                    field_key="container_number",
                    field_label="Container Number",
                    field_value="MSKU-999910",
                    raw_value="MSKU-999910",
                    confidence_score=98.3,
                    is_low_confidence=False,
                    is_confirmed=True,
                    bounding_box={"page": 1, "x": 60, "y": 340, "w": 180, "h": 24}
                ),
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="packages",
                    field_key="seal_number",
                    field_label="Carrier Seal Number",
                    field_value="SL-999901",
                    raw_value="SL-999901",
                    confidence_score=97.0,
                    is_low_confidence=False,
                    is_confirmed=True,
                    bounding_box={"page": 1, "x": 260, "y": 340, "w": 150, "h": 24}
                ),
                ExtractedField(
                    shipment_id=shipment_id,
                    document_id=doc_id,
                    field_group="weights",
                    field_key="bl_gross_weight",
                    field_label="BL Carrier Gross Weight (kg)",
                    field_value="15000.00",
                    raw_value="15,000.00 KGS",
                    confidence_score=99.1,
                    is_low_confidence=False,
                    is_confirmed=True,
                    bounding_box={"page": 1, "x": 500, "y": 340, "w": 170, "h": 26}
                ),
            ]

        return [
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="metadata",
                field_key="bl_number",
                field_label="Bill of Lading Number",
                field_value="MAEU92837190",
                raw_value="MAEU-92837190",
                confidence_score=99.1,
                is_low_confidence=False,
                is_confirmed=True,
                bounding_box={"page": 1, "x": 520, "y": 60, "w": 190, "h": 24}
            ),
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="parties",
                field_key="bl_shipper_name",
                field_label="Shipper / Exporter",
                field_value="Shenzhen Precision Microelectronics Co., Ltd.",
                raw_value="Shenzhen Precision Microelectronics Co., Ltd.",
                confidence_score=98.0,
                is_low_confidence=False,
                is_confirmed=True,
                bounding_box={"page": 1, "x": 60, "y": 100, "w": 300, "h": 32}
            ),
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="parties",
                field_key="bl_consignee_name",
                field_label="Consignee",
                field_value="Apex Logistics Global LLC",
                raw_value="Apex Logistics Global LLC",
                confidence_score=97.8,
                is_low_confidence=False,
                is_confirmed=True,
                bounding_box={"page": 1, "x": 60, "y": 160, "w": 300, "h": 32}
            ),
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="metadata",
                field_key="bl_vessel_voyage",
                field_label="Ocean Vessel / Voyage",
                field_value="EVER GIVEN / 0428-091W",
                raw_value="EVER GIVEN V. 0428-091W",
                confidence_score=96.7,
                is_low_confidence=False,
                is_confirmed=True,
                bounding_box={"page": 1, "x": 60, "y": 240, "w": 250, "h": 22}
            ),
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="metadata",
                field_key="bl_port_of_discharge",
                field_label="Port of Discharge",
                field_value="Port of Los Angeles, US",
                raw_value="PORT OF LOS ANGELES, USA",
                confidence_score=97.0,
                is_low_confidence=False,
                is_confirmed=True,
                bounding_box={"page": 1, "x": 380, "y": 240, "w": 220, "h": 22}
            ),
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="packages",
                field_key="container_number",
                field_label="Container Number",
                field_value="MSKU9281745",
                raw_value="MSKU9281745",
                confidence_score=98.3,
                is_low_confidence=False,
                is_confirmed=True,
                bounding_box={"page": 1, "x": 60, "y": 340, "w": 180, "h": 24}
            ),
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="packages",
                field_key="seal_number",
                field_label="Carrier Seal Number",
                field_value="SL-839201",
                raw_value="SL-839201",
                confidence_score=96.0,
                is_low_confidence=False,
                is_confirmed=True,
                bounding_box={"page": 1, "x": 260, "y": 340, "w": 150, "h": 24}
            ),
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="weights",
                field_key="bl_gross_weight",
                field_label="BL Carrier Gross Weight (kg)",
                field_value="12800.00",
                raw_value="12,800.00 KGS",
                confidence_score=99.1,
                is_low_confidence=False,
                is_confirmed=True,
                bounding_box={"page": 1, "x": 500, "y": 340, "w": 170, "h": 26}
            ),
        ]

    @classmethod
    def _extract_generic(cls, shipment_id: int, doc_id: int) -> List[ExtractedField]:
        return [
            ExtractedField(
                shipment_id=shipment_id,
                document_id=doc_id,
                field_group="metadata",
                field_key="document_title",
                field_label="Document Title",
                field_value="Supplementary Logistics Document",
                confidence_score=92.0,
                is_low_confidence=False,
                is_confirmed=True
            )
        ]