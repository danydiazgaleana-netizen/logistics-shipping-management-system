Logistics Order & Shipment Microservice API
Backend service developed with FastAPI and SQLite designed for the ingestion, validation, and end-to-end traceability of Sales Orders (OV - Órdenes de Venta) and shipping processes.

This project simulates a core component of an Enterprise Resource Planning (ERP) or Warehouse Management System (WMS), enforcing strict data integrity rules, audit trails, and automated testing protocols.

🚀 Key Features
Master Key Validation (OV): Uses Sales Order numbers as unique primary identifiers to prevent conflicting records.

Idempotency & Business Logic Guardrails: Validates against duplicate insertions (HTTP 400) to maintain inventory and order accuracy.

Automated Audit Logging: Every transactional event (CREATE_EMBARQUE) automatically generates an immutable audit log with timestamps for compliance and process tracking.

Robust Test Coverage: Fully tested suite using pytest and FastTestClient, covering positive assertions, boundary conditions (duplicates), and error handling (HTTP 201, 400, 404, 500).

🛠️ Tech Stack
Backend Framework: FastAPI (Python)

Database: SQLite with relational constraints and custom row factories

Data Validation: Pydantic v2 (strict typing, field constraints like gt=0)

Testing: Pytest, HTTPX

📦 API Endpoints
1. Register a New Shipment
Endpoint: POST /api/embarques

Status Codes:

201 Created: Successfully registered and logged.

400 Bad Request: Sales Order (OV) already exists.

Payload Example:

JSON
{
  "ov": "OV-TEST-999",
  "numero_pedido": "PED-TEST",
  "cliente": "Global Retail Corp",
  "cajas": 10,
  "valor": 1250.00
}
2. Retrieve Shipment by OV
Endpoint: GET /api/embarques/{ov}

Status Codes:

200 OK: Returns complete shipment details and current status.

404 Not Found: Order does not exist in the system.

🧪 Running Tests
To verify the test suite and ensure zero regression failures across the logistics logic, execute:

Bash
pytest -v
