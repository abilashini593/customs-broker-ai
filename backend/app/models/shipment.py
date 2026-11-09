import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    shipment_number = Column(String(50), unique=True, index=True, nullable=False)
    supplier_name = Column(String(255), nullable=False)
    supplier_country = Column(String(100), nullable=False)
    consignee_name = Column(String(255), nullable=False)
    consignee_country = Column(String(100), default="United States")
    port_of_loading = Column(String(150), nullable=False)
    port_of_discharge = Column(String(150), nullable=False)
    vessel_name = Column(String(150), nullable=True)
    voyage_number = Column(String(100), nullable=True)
    status = Column(String(50), default="Pending Review")  # Pending Review, Cross-Check Failed, Cleared, Exported
    total_declared_value = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    documents = relationship("Document", back_populates="shipment", cascade="all, delete-orphan")
    extracted_fields = relationship("ExtractedField", back_populates="shipment", cascade="all, delete-orphan")
    line_items = relationship("LineItem", back_populates="shipment", cascade="all, delete-orphan")
    cross_checks = relationship("CrossCheckResult", back_populates="shipment", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="shipment", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)
    doc_type = Column(String(50), nullable=False)  # commercial_invoice, packing_list, bill_of_lading
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    mime_type = Column(String(100), default="application/pdf")
    page_count = Column(Integer, default=1)
    parsed_text = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    shipment = relationship("Shipment", back_populates="documents")
    fields = relationship("ExtractedField", back_populates="document", cascade="all, delete-orphan")


class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    field_group = Column(String(50), nullable=False)  # parties, metadata, weights, packages, valuation
    field_key = Column(String(100), nullable=False)   # e.g., invoice_gross_weight, consignee_name
    field_label = Column(String(150), nullable=False)
    field_value = Column(String(500), nullable=False)
    raw_value = Column(String(500), nullable=True)    # Original OCR extraction before edit
    confidence_score = Column(Float, default=95.0)    # 0 - 100
    is_low_confidence = Column(Boolean, default=False)
    is_confirmed = Column(Boolean, default=False)
    confirmed_by = Column(String(100), nullable=True)
    bounding_box = Column(JSON, nullable=True)        # {page: 1, x: 120, y: 340, w: 200, h: 25}

    shipment = relationship("Shipment", back_populates="extracted_fields")
    document = relationship("Document", back_populates="fields")


class LineItem(Base):
    __tablename__ = "line_items"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)
    item_number = Column(Integer, nullable=False)
    description = Column(String(300), nullable=False)
    hsn_code = Column(String(50), nullable=False)     # Harmonized System / Tariff code
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), default="PCS")
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    confidence_score = Column(Float, default=96.0)
    is_confirmed = Column(Boolean, default=False)

    shipment = relationship("Shipment", back_populates="line_items")


class CrossCheckResult(Base):
    __tablename__ = "cross_check_results"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)
    rule_code = Column(String(80), nullable=False)
    rule_name = Column(String(200), nullable=False)
    severity = Column(String(20), default="BLOCKER")   # BLOCKER, WARNING, INFO
    status = Column(String(20), default="PASSED")     # PASSED, FAILED, OVERRIDDEN
    message = Column(Text, nullable=False)
    discrepancy_details = Column(JSON, nullable=True)
    is_blocking = Column(Boolean, default=True)
    override_reason = Column(Text, nullable=True)
    overridden_by = Column(String(100), nullable=True)
    overridden_at = Column(DateTime, nullable=True)

    shipment = relationship("Shipment", back_populates="cross_checks")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)
    user_role = Column(String(50), nullable=False)     # Documentation Executive, Documentation Manager, System
    user_name = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)       # FIELD_CONFIRMED, OVERRIDE_APPLIED, EXPORTED, etc.
    details = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.now)

    shipment = relationship("Shipment", back_populates="audit_logs")
