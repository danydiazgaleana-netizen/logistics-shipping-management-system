# Cross-Functional Logistics and Shipping Management System

## 🚀 Overview
A data-driven logistics operations and shipping management system developed in Python. Designed to automate and streamline order fulfillment, tracking, data validation, and documentation processes across cross-functional supply chain environments.

---

## 📊 Sample Data: Maestro de Embarques (Cleaned Data)
A snippet of the structured operational dataset stored in `data/maestro_embarques_dummy.csv`, handling transactional tracking, carrier assignment, and financial values:

| OV | Número de Pedido | Cliente | Cajas | Bolsas | Fecha de Salida | Ubicación | Paquetería | Valor (MXN) | Estancia (Días) | Guía |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| 2003268.0 | PEGE2026-498-2003268 | Cliente A | 12.0 | 2.0 | 2026-07-26 | Puebla | DHL | $15,000.50 | 1.0 | GUIA-DHL-88901 |
| 2003269.0 | PEGE2026-499-2003269 | Cliente B | 8.0 | 1.0 | 2026-07-26 | CDMX | FedEx | $8,400.00 | 2.0 | GUIA-FDX-44210 |
| 2003270.0 | PEGE2026-500-2003270 | Cliente C | 15.0 | 4.0 | 2026-07-27 | Monterrey | Estafeta | $22,100.00 | 0.0 | GUIA-EST-11293 |

---

## 📈 Automated Analytics & KPI Report
Running the built-in analytics engine (`core/analitica_embarques.py`) processes the master dataset to output real-time supply chain metrics:

```text
--- REPORTE DE ANALÍTICA DE EMBARQUES ---
Total de embarques procesados: 3

⏱️ Promedio de días de estancia: 1.00 días
💰 Valor total de la mercancía: $45,500.50 MXN

📦 Volumen de envíos por Paquetería:
   - DHL: 1 embarque(s)
   - FedEx: 1 embarque(s)
   - Estafeta: 1 embarque(s)

📍 Destinos principales:
   - Puebla: 1 envío(s)
   - CDMX: 1 envío(s)
   - Monterrey: 1 envío(s)

🗂️ Project Structure
Plaintext
simulacion_logistica/
│
├── core/                  # Business logic, data validation, and analytics engines
│   └── analitica_embarques.py
├── data/                  # Operational logs, error audits, and master shipping CSVs
│   └── maestro_embarques_dummy.csv
├── gui/                   # User interface and dashboard logic
├── guias_maestras/        # Official documentation and waybill templates
└── README.md              # Project documentation
🛠️ Tech Stack
Language: Python

Data Processing: Pandas / NumPy

Automation & GUI: Custom Python GUI modules & scripting

Version Control: Git & GitHub
