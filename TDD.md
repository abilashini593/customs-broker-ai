# Technical Design Document (TDD)
## Project 1: Customs Broker's AI Document Extraction & Cross-Check Tool
**Platform Name:** ClearBorder AI Enterprise  
**System Specification:** Single Window Customs Automation Engine (v4.2)  
**Author:** Principal Software Engineer & Full-Stack Architect  
**Status:** Approved for Production Deployment  

---

### 1. Executive Summary & Problem Space
Customs brokerage firms and freight forwarders process thousands of multi-jurisdictional shipping dockets daily. Each consignment requires cross-referencing at least three distinct documents:
1. **Commercial Invoice** (values, line items, currency, terms, declared weights)
2. **Packing List** (gross/net cargo weights, tare, pallets/cartons, container & seal numbers)
3. **Bill of Lading / Air Waybill** (carrier manifest, vessel/voyage, carrier gross weight, port of loading/discharge, consignee name)

Manual human reconciliation is slow (20–45 minutes per docket) and vulnerable to human fatigue. Even minor discrepancies (e.g., a 2.8% gross weight variance between the carrier scale and the packing list) can cause customs border holds, demurrage penalties ($300+/day/container), or severe trade compliance penalties.

**ClearBorder AI** provides an automated, deterministic verification platform that ingests multi-format documents via Vision AI, normalizes complex trade units, highlights low-confidence OCR fields with smart badges, and runs strict deterministic cross-checks that block invalid customs declarations from export.

---

### 2. High-Level System Architecture

```mermaid
flowchart TD
    subgraph Ingestion["1. Ingestion Layer"]
        Upload["Document Upload Modal\n(Multi-file: Invoice, PL, BL)"] --> OCR["Vision AI Parser\n(Layout, Tables, Bounding Boxes)"]
    end

    subgraph Extraction["2. Extraction & Normalization"]
        OCR --> EntityMap["Entity & Line Item Normalizer\n(HSN, Qty, Prices, Currencies)"]
        OCR --> WeightNorm["Weight & Unit Normalizer\n(Metric kg <-> lbs conversions)"]
        OCR --> BBox["Bounding Box Mapper\n(x, y, w, h coordinates)"]
    end

    subgraph DeterministicEngine["3. Deterministic Cross-Check Engine"]
        EntityMap --> Rule1["Rule 1: Line Items Sum == Invoice Grand Total"]
        WeightNorm --> Rule2["Rule 2: Gross Weight Consistency across Invoice, PL, BL"]
        EntityMap --> Rule3["Rule 3: Consignee & Port Consistency"]
        EntityMap --> Rule4["Rule 4: Container & Seal Consistency"]
        EntityMap --> Rule5["Rule 5: HSN Tariff Code Format Validity"]
    end

    subgraph CoreUI["4. SaaS Review Workspace"]
        Rule1 & Rule2 & Rule3 & Rule4 & Rule5 --> ValidationCard["Deterministic Cross-Check Card\n(Passed / Low-Conf / Blocker)"]
        BBox --> SideBySide["Side-by-Side Review Screen\n(Interactive Doc + Structured Accordion)"]
    end

    subgraph RoleAndExport["5. Governance & Export Engine"]
        SideBySide --> RoleSwitch{"Role Switcher"}
        RoleSwitch -->|Documentation Executive| EditConfirm["Edit & Confirm Fields\n(Clear Low-Confidence Flags)"]
        RoleSwitch -->|Documentation Manager| OverrideModal["Manager Override Approval\n(Mandatory Audit Justification)"]
        EditConfirm & OverrideModal --> ExportEngine["Customs Filing Generator\n(Single Window / ICEGATE / US CBP ACE)"]
        ExportEngine --> AuditLog["Immutable Audit Trail & Digital Seal"]
    end
```

---

### 3. Core Relational Data Model (SQLite / PostgreSQL)

The data layer uses normalized relational tables:

```mermaid
erDiagram
    SHIPMENTS ||--o{ DOCUMENTS : contains
    SHIPMENTS ||--o{ EXTRACTED_FIELDS : maps
    SHIPMENTS ||--o{ LINE_ITEMS : items
    SHIPMENTS ||--o{ CROSS_CHECK_RESULTS : validates
    SHIPMENTS ||--o{ AUDIT_LOGS : records

    SHIPMENTS {
        int id PK
        string shipment_number UK
        string supplier_name
        string supplier_country
        string consignee_name
        string port_of_loading
        string port_of_discharge
        string vessel_name
        string voyage_number
        string status
        float total_declared_value
        string currency
        datetime created_at
        datetime updated_at
    }

    DOCUMENTS {
        int id PK
        int shipment_id FK
        string doc_type
        string file_name
        string file_path
        int file_size
        string mime_type
        int page_count
        datetime uploaded_at
    }

    EXTRACTED_FIELDS {
        int id PK
        int shipment_id FK
        int document_id FK
        string field_group
        string field_key
        string field_label
        string field_value
        string raw_value
        float confidence_score
        boolean is_low_confidence
        boolean is_confirmed
        string confirmed_by
        json bounding_box
    }

    LINE_ITEMS {
        int id PK
        int shipment_id FK
        int item_number
        string description
        string hsn_code
        float quantity
        string unit
        float unit_price
        float total_amount
        string currency
        float confidence_score
        boolean is_confirmed
    }

    CROSS_CHECK_RESULTS {
        int id PK
        int shipment_id FK
        string rule_code
        string rule_name
        string severity
        string status
        string message
        json discrepancy_details
        boolean is_blocking
        string override_reason
        string overridden_by
        datetime overridden_at
    }

    AUDIT_LOGS {
        int id PK
        int shipment_id FK
        string user_role
        string user_name
        string action
        string details
        datetime timestamp
    }
```

---

### 4. Deterministic Cross-Check Business Rules

The system implements 5 mathematical verification rules:

1. **Rule 1: Line Items Sum vs Invoice Grand Total (`RULE_INVOICE_TOTAL_SUM`)**
   - Formula:
     $$\Delta = \left| \sum_{i=1}^{n} (\text{Qty}_i \times \text{Unit Price}_i) - \text{Invoice Grand Total} \right|$$
   - Tolerance threshold: $\Delta \le \$0.10$ (standard currency rounding).
   - If $\Delta > \$0.10$: Status set to `FAILED`, `is_blocking = True`.

2. **Rule 2: Multi-Document Gross Weight Consistency (`RULE_GROSS_WEIGHT_CONSISTENCY`)**
   - Gathers normalized gross weights $W_{\text{INV}}, W_{\text{PL}}, W_{\text{BL}}$ in kg.
   - Calculates absolute variance: $\Delta_W = \max(W) - \min(W)$
   - Calculates percentage variance: $P_W = \frac{\Delta_W}{\min(W)} \times 100\%$
   - Tolerance: $\Delta_W \le 5.0\text{ kg}$ OR $P_W \le 0.5\%$.
   - Any variance exceeding tolerance triggers a high-contrast rose blocker, preventing declaration export.

3. **Rule 3: Consignee & Port of Discharge Consistency (`RULE_CONSIGNEE_PORT_MATCH`)**
   - Normalizes legal entity names by stripping corporate suffixes (`LLC`, `Inc.`, `Corp.`, `GmbH`, `AB`).
   - Reconciles Consignee and Destination Port between the Commercial Invoice and the Carrier Bill of Lading.

4. **Rule 4: Container & Carrier Seal Integrity (`RULE_CONTAINER_SEAL_MATCH`)**
   - Validates ISO 6346 container numbers (e.g. `MSKU9281745`) and high-security bolt seals across Packing List and BL.

5. **Rule 5: HSN / Tariff Classification Code Format (`RULE_HSN_FORMAT`)**
   - Enforces 6 to 10-digit international Harmonized System tariff codes for every single line item.

---

### 5. Role-Based Governance & Manager Override Workflow

To balance automation with human-in-the-loop compliance:
- **Documentation Executive:**
  - Performs document ingestion and reviews OCR extractions.
  - Resolves low-confidence fields (<85%) with 1-click confirmation or direct edits.
  - Re-triggers real-time deterministic cross-checks upon editing.
  - Cannot export or bypass active cross-check failures.
- **Documentation Manager:**
  - Possesses elevated authority.
  - Can apply formal **Manager Overrides** to non-fatal discrepancies (e.g. carrier tare scale differences) by submitting a mandatory compliance justification.
  - Authorizes and executes the final Customs Filing EDI Export.

---

### 6. Architectural Trade-offs & What Was Cut

| Decision | Chosen Approach | Alternative Considered | Rationale |
| :--- | :--- | :--- | :--- |
| **Database** | SQLite with SQLAlchemy ORM | PostgreSQL / CockroachDB | Zero-friction local setup, instant pre-seeded startup with zero Docker prerequisites. Ready to switch to PostgreSQL via single `DATABASE_URL` env variable. |
| **Cross-Check Execution** | Deterministic Python Rule Engine | LLM-based Cross-Check Prompts | Customs compliance requires 100% mathematical certainty, reproducible tolerances, and zero hallucination risk. |
| **Document Highlighting** | Client-side Vector Bounding Boxes | Server-side image rendering | Zero server CPU latency during zoom/pan; crisp high-DPI interactive highlighting. |
| **What Was Cut** | Full OCR GPU model training pipeline | Cloud Vision API integration | Production tool includes a mock Vision AI pipeline with realistic bounding boxes and confidence scores to allow full local evaluation without proprietary cloud API keys. |

---

### 7. Security & Audit Trail Integrity
- Every edit, confirmation, override, and export is recorded in the `audit_logs` table with timestamp, user role, and audit description.
- Exports include a SHA-256 digital integrity seal generated over the shipment manifest metadata.
