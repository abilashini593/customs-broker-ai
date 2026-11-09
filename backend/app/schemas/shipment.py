import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Extracted Field Schemas
class ExtractedFieldBase(BaseModel):
    field_group: str
    field_key: str
    field_label: str
    field_value: str
    raw_value: Optional[str] = None
    confidence_score: float = 95.0
    is_low_confidence: bool = False
    is_confirmed: bool = False
    confirmed_by: Optional[str] = None
    bounding_box: Optional[Dict[str, Any]] = None

class ExtractedFieldUpdate(BaseModel):
    field_value: str
    is_confirmed: bool = True
    confirmed_by: Optional[str] = "Documentation Executive"

class ExtractedFieldResponse(ExtractedFieldBase):
    id: int
    shipment_id: int
    document_id: Optional[int] = None

    class Config:
        from_attributes = True

# Line Item Schemas
class LineItemBase(BaseModel):
    item_number: int
    description: str
    hsn_code: str
    quantity: float
    unit: str = "PCS"
    unit_price: float
    total_amount: float
    currency: str = "USD"
    confidence_score: float = 96.0
    is_confirmed: bool = False

class LineItemUpdate(BaseModel):
    description: Optional[str] = None
    hsn_code: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    total_amount: Optional[float] = None
    is_confirmed: Optional[bool] = True

class LineItemResponse(LineItemBase):
    id: int
    shipment_id: int

    class Config:
        from_attributes = True

# Document Schemas
class DocumentResponse(BaseModel):
    id: int
    shipment_id: int
    doc_type: str
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    page_count: int
    uploaded_at: datetime.datetime
    parsed_text: Optional[str] = None

    class Config:
        from_attributes = True

# Cross Check Schemas
class CrossCheckResultResponse(BaseModel):
    id: int
    shipment_id: int
    rule_code: str
    rule_name: str
    severity: str
    status: str
    message: str
    discrepancy_details: Optional[Dict[str, Any]] = None
    is_blocking: bool
    override_reason: Optional[str] = None
    overridden_by: Optional[str] = None
    overridden_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

class CrossCheckSummary(BaseModel):
    total_rules: int
    passed_rules: int
    failed_rules: int
    overridden_rules: int
    has_blocking_discrepancy: bool
    is_export_ready: bool
    results: List[CrossCheckResultResponse]

class ManagerOverrideRequest(BaseModel):
    rule_code: str
    override_reason: str = Field(..., min_length=10, description="Mandatory audit justification for manager override")
    manager_name: str = "Sarah Chen (Documentation Manager)"

# Audit Log Schemas
class AuditLogResponse(BaseModel):
    id: int
    shipment_id: int
    user_role: str
    user_name: str
    action: str
    details: str
    timestamp: datetime.datetime

    class Config:
        from_attributes = True

# Shipment Schemas
class ShipmentBase(BaseModel):
    shipment_number: str
    supplier_name: str
    supplier_country: str
    consignee_name: str
    consignee_country: str = "United States"
    port_of_loading: str
    port_of_discharge: str
    vessel_name: Optional[str] = None
    voyage_number: Optional[str] = None
    total_declared_value: float = 0.0
    currency: str = "USD"
    notes: Optional[str] = None

class ShipmentCreate(ShipmentBase):
    pass

class ShipmentListItem(BaseModel):
    id: int
    shipment_number: str
    supplier_name: str
    supplier_country: str
    consignee_name: str
    port_of_loading: str
    port_of_discharge: str
    status: str
    total_declared_value: float
    currency: str
    document_count: int
    low_confidence_count: int
    cross_check_status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class ShipmentDetailResponse(ShipmentBase):
    id: int
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    documents: List[DocumentResponse] = []
    extracted_fields: List[ExtractedFieldResponse] = []
    line_items: List[LineItemResponse] = []
    cross_checks: List[CrossCheckResultResponse] = []
    audit_logs: List[AuditLogResponse] = []

    class Config:
        from_attributes = True

class ExportRequest(BaseModel):
    format: str = "csv" # csv, xlsx, json
    system_target: str = "ICEGATE_US_CBP_ACE"
    user_role: str = "Documentation Manager"
    user_name: str = "Sarah Chen"
