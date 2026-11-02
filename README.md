# TourPlus AI — Personalized Medical Tourism Platform

> **TourPlus AI** is an AI-assisted, patient-centric decision-support platform designed for international patients traveling to India for healthcare. It unifies medical service discovery, hospital-specific financial planning, recovery-aware tourism recommendations, and travel-agency package matching into a single, explainable, and auditable itinerary.

---

## Key Pillars

1. **Medical Service Discovery**: Curated, verified hospital treatment offerings across **Cardiology**, **Orthopedics**, and **Oncology**.
2. **Hospital-Specific Financial Scenarios**: Separate planning scenarios for each eligible hospital city with exact Python `Decimal` ledger accounting (treatment, flights, recovery lodging, visas, transfers, contingency reserves).
3. **Recovery-Aware 3-Tier Tourism Hierarchy**: Sightseeing recommendations stratified into **Local/Regional**, **State-Level**, and **National/Pan-India** tiers, governed by medical recovery duration and treating clinician travel guidance.
4. **Dynamic Package Matching & Inclusion Credit**: Automated matching of travel-agency packages with the **Dynamic Inclusion Credit** ($EPC_p = P_p - I_p$) that prevents double-counting of mandatory expenses.
5. **Explainable Plan Generation & Provenance**: End-to-end auditability, reproducible recommendation runs, transparent ranking weights, and explicit labeling of **Verified** vs. **Indicative** data.

---

## Technology Stack

- **Frontend**: Next.js 15 (App Router), React 18, TypeScript, Tailwind CSS, Lucide Icons.
- **Backend**: Django 5.2 LTS, Django REST Framework (DRF), PostgreSQL / PostGIS spatial database.
- **Engines**: Deterministic multi-criteria decision making (MCDM), Haversine spatial routing engine, Decimal financial ledger.
- **AI / LLM Integration**: Pluggable provider abstraction with graceful deterministic fallback.

---

## Repository Structure

```text
TourPlus/
├── backend/                       # Django 5.2 LTS REST API monolith
│   ├── apps/                      # Domain modular applications (accounts, geography, medical, hospitals, etc.)
│   ├── engines/                   # Core business logic (budgeting, hospitals, tourism, package_matching)
│   ├── integrations/              # External services (maps, exchange rates, LLM)
│   ├── common/                    # Shared permissions, pagination, validators, exceptions
│   ├── requirements/              # Python dependencies (base.txt, dev.txt, prod.txt)
│   └── tests/                     # Automated unit, integration, and E2E test suite
├── frontend/                      # Next.js 15 App Router web client
│   ├── src/app/                   # Routes ((public), (auth), (patient) dashboard, wizard, scenarios, final plan)
│   ├── src/components/            # UI component library, layouts, feedback modals
│   ├── src/lib/                   # API client, currency formatting, duration helpers
│   └── src/types/                 # Centralized TypeScript interfaces
├── docs/                          # Architectural Decision Records & technical documentation
│   ├── architecture.md
│   ├── database-schema.md
│   ├── api-contracts.md
│   ├── recommendation-methodology.md
│   ├── financial-model.md
│   ├── security-and-privacy.md
│   └── decisions/                 # ADR-001, ADR-002, ADR-003
├── scripts/                       # Management and validation scripts
│   ├── seed_demo_data.py          # Seed curated catalogue
│   └── validate_catalogue.py      # Verify database invariants
├── PRODUCT.md                     # Product requirements and source of truth
└── implementation_plan.md         # Master implementation roadmap and checklist
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+ and `pnpm`
- PostgreSQL 16 with PostGIS extension (or local SQLite for dev)

### 1. Backend Setup

```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements/dev.txt
python manage.py migrate
python manage.py seed_catalogue
python manage.py runserver
```

The backend API will be available at `http://localhost:8000/api/v1/`.

### 2. Frontend Setup

```bash
cd frontend
pnpm install
pnpm run dev
```

The web application will be accessible at `http://localhost:3000/`.

---

## Automated Verification & Testing

### Run Backend Test Suite
```bash
cd backend
python manage.py test tests
```
*Executes all 15 automated test suites covering authentication, catalogue APIs, MCDM hospital ranking, Decimal budget ledger, 3-tier tourism engine, package inclusion credits, and end-to-end plan generation.*

### Run Catalogue Integrity Check
```bash
python scripts/validate_catalogue.py
```

### Run Frontend Production Build
```bash
cd frontend
pnpm run build
```

---

## Safety & Medical Disclaimers

> **IMPORTANT MEDICAL NOTICE**: TourPlus AI provides non-clinical administrative and logistical decision support only. It is **not** a licensed medical provider and does **not** provide diagnoses, treatment prescriptions, or clinical triage. All surgical procedures, clinical recovery schedules, and travel feasibility clearances must be approved by the patient's treating physician.

---

## License

Proprietary © 2026 TourPlus AI. All rights reserved.

