# Cross-Functional Logistics and Shipping Management System

## 🚀 Overview
A data-driven logistics operations and shipping management system developed in Python. Designed to automate and streamline order fulfillment, tracking, data validation, and documentation processes across cross-functional supply chain environments.

## 📊 Core Features & Architecture
- **Order & Shipping Management:** Centralized processing of operational orders (`OV`), tracking metrics, package counts (boxes/bags), and transit times.
- **Data Validation & Error Auditing:** Automated validation scripts (`core/validador.py`, `core/conciliador_rev.py`) to catch shipping discrepancies and log errors in real-time.
- **Traceability & Document Control:** Manages carrier assignments (DHL, FedEx, Estafeta), driver handoffs, delivery schedules, and digital waybill linkages (`Numero de guia`, `Archivo guia`).
- **Analytics & BI-Ready Datasets:** Structured data schemas (`data/maestro_embarques_dummy.csv`) built to feed supply chain performance metrics (Lead times, fulfillment status, and carrier performance).

## 🗂️ Project Structure
```text
simulacion_logistica/
│
├── core/                  # Business logic, data validation, and PDF readers
├── data/                  # Operational logs, error audits, and master shipping CSVs
├── gui/                   # User interface and dashboard logic
├── guias_maestras/        # Official documentation and waybill templates
└── app_dashboard.py       # Main dashboard application entry point
