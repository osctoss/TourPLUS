# TourPlus AI — Medical Tourism Decision-Support Platform

<div align="center">

[![Next.js](https://img.shields.io/badge/Next.js-15.1-black?logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-18.3-blue?logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue?logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?logo=tailwind-css)](https://tailwindcss.com/)
[![Django](https://img.shields.io/badge/Django-5.2_LTS-092E20?logo=django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/DRF-3.15-red)](https://www.django-rest-framework.org/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL_%2B_PostGIS-3ECF8E?logo=supabase)](https://supabase.com/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-15%20Passed-success)](#automated-testing--verification)
[![License](https://img.shields.io/badge/License-Proprietary-darkred)](#license)

**An AI-assisted, patient-centric decision-support platform for personalized medical tourism in India.**

[Key Features](#key-features) • [Architecture](#system-architecture) • [Financial Mathematics](#financial--recommendation-mathematics) • [Quickstart](#quickstart-guide) • [Supabase Setup](#database--supabase-integration) • [API Contracts](#api-contracts) • [Testing](#automated-testing--verification) • [Medical Disclaimers](#medical--financial-disclaimers)

</div>

---

## Executive Overview

Planning an international medical journey is a fragmented, high-stakes process. Prospective patients must coordinate hospitals, accredited clinical specialties, foreign travel visas, international airfare, recovery lodging, local transport, post-procedure tourism, and travel agency packages across multiple disconnected intermediaries.

**TourPlus AI** unifies this journey into a single, deterministic, and explainable decision framework. The platform evaluates patient medical requirements, travel party sizes, and budgets to generate **discrete, parallel scenarios for each eligible hospital city**. 

Unlike generic directories or booking aggregators, TourPlus AI solves the critical **double-counting problem**: when an agency package includes hotel nights or international airfare already accounted for in mandatory expenses, TourPlus AI credits those inclusions against the ledger to calculate the **true effective incremental package cost** ($EPC_p$).

---

## Key Features

1. **Verified Medical Service Discovery**
   - Curated clinical offerings across three core specialties: **Cardiology**, **Orthopedics**, and **Oncology**.
   - Clear classification of procedure offerings: `VERIFIED` (hospital-confirmed), `INDICATIVE` (curated baseline), and `DEMO`.
   - International patient support tracking (visas, airport transfers, multi-lingual interpreters).

2. **Hospital-Specific Financial Scenarios**
   - Generates independent, non-aggregated financial planning scenarios for every eligible hospital city.
   - Deterministic calculations powered entirely by Python `Decimal` objects (avoiding floating-point rounding errors).
   - Accurate cost ranges ($ME_{min}, ME_{expected}, ME_{max}$) and automatic **Over-Budget Shortfall** state detection ($|DB_{0,s}|$).

3. **Recovery-Aware 3-Tier Tourism Hierarchy**
   - Sightseeing recommendations stratified into three geographic and temporal scopes:
     - **Local / Regional**: Within 100 km / 2 hours transit of the hospital city.
     - **State-Level**: Within the same Indian state or up to 350 km transit.
     - **National / Pan-India**: Inter-state destinations permitted only when duration, budget, and clinical recovery allow.
   - **Clinical Recovery Boundary**: Destinations requiring physical exertion are flagged with `REQUIRES_CLINICAL_REVIEW` unless cleared by the treating physician.

4. **Dynamic Package Matching & Inclusion Credit Ledger**
   - Matches agency travel packages against recommended destinations.
   - **Dynamic Package Inclusion Credit ($EPC_p = P_p - I_p$)**: Eliminates double-counting of mandatory expenses (flights, lodging, transfers) included in agency tour packages.
   - Prorates hotel nights, normalizes party sizes, and prevents crediting of non-budgeted activities (sightseeing/meals).

5. **Final Plan Synthesis & Printable Export**
   - Saves patient-selected hospital scenarios, customized destination itineraries, and chosen packages into a permanent `FinalPlan`.
   - Clean `@media print` optimized printable view for offline medical consultations.
   - Complete audit trail and provenance tracking for regulatory compliance and trust.

---

## System Architecture

```mermaid
flowchart TD
    subgraph Client ["Frontend Client (Next.js 15 App Router)"]
        UI_Home["Landing & How It Works"]
        UI_Auth["Patient Auth & Profile"]
        UI_Wizard["6-Step Assessment Wizard"]
        UI_Results["Hospital Scenarios Dashboard"]
        UI_Budget["Scenario Budget Ledger UI"]
        UI_Tourism["3-Tier Tourism Explorer"]
        UI_Packages["Package Matching & Credit UI"]
        UI_Plan["Final Plan View & Print Export"]
    end

    subgraph Backend ["Backend API Monolith (Django 5.2 LTS + DRF)"]
        Gateway["REST API Gateway (/api/v1/)"]
        App_Accounts["apps.accounts (User UUID, Profiles, Consents)"]
        App_Geo["apps.geography (Countries, States, Cities, FX)"]
        App_Medical["apps.medical & apps.hospitals (Specialties, Offerings, Costs)"]
        App_Tourism["apps.tourism (Destinations, Travel Limits)"]
        App_Packages["apps.agencies & apps.packages (Packages, Inclusions)"]
        App_Planning["apps.trip_planning (Trip Requests, Snapshots)"]
        App_Rec["apps.recommendations (Runs, Scenarios, Audits)"]
        App_Final["apps.final_plans (Final Plans, Itineraries)"]

        subgraph Engines ["Deterministic Calculation Engines"]
            Eng_Hospital["engines.hospitals (Hard Filters + MCDM Ranking)"]
            Eng_Budget["engines.budgeting (Decimal Ledger & Shortfall)"]
            Eng_Tourism["engines.tourism (3-Tier Scope & Recovery Bounds)"]
            Eng_Package["engines.package_matching (Inclusion Credit Ledger)"]
        end

        subgraph Integrations ["External Service Adapters"]
            Integ_Maps["integrations.maps (Routes API + Haversine Fallback)"]
            Integ_FX["integrations.exchange_rates (Curated & Live FX)"]
            Integ_LLM["integrations.llm (Gemini / OpenAI + Fallback)"]
        end
    end

    subgraph DataStore ["Database Layer (Supabase / PostgreSQL + PostGIS)"]
        DB[(PostgreSQL System of Record)]
        Spatial[(PostGIS Spatial Indices)]
    end

    Client <-->|REST API / JSON / Tokens| Gateway
    Gateway --> App_Accounts & App_Planning & App_Rec & App_Final
    App_Rec --> Eng_Hospital & Eng_Budget & Eng_Tourism & Eng_Package
    Eng_Tourism --> Integ_Maps
    Eng_Budget --> Integ_FX
    App_Rec --> Integ_LLM
    Eng_Hospital & Eng_Budget & Eng_Tourism & Eng_Package --> DB & Spatial
```

---

## Financial & Recommendation Mathematics

All financial calculations strictly follow the deterministic formulas defined in `PRODUCT.md`:

### 1. Mandatory Expenditure ($ME_s$)
For each hospital scenario $s$:
$$ME_s = TC_s + FC_s + HC_s + VC_s + LC_s + MC_s$$

Where:
- $TC_s$: Medical procedure cost at offering hospital.
- $FC_s$: International return airfare ($FC_s = \text{FlightUnit} \times \text{PartySize}$).
- $HC_s$: Medical recovery lodging ($HC_s = \text{NightlyRate} \times \text{StayNights} \times \lceil\text{PartySize}/2\rceil$).
- $VC_s$: Medical visa processing fees ($VC_s = \text{VisaUnit} \times \text{PartySize}$).
- $LC_s$: Local dedicated transfers (airport, hospital, lodging).
- $MC_s$: Incidentals and pharmacy contingency reserve.

### 2. Discretionary Budget & Over-Budget Shortfall
$$DB_{0,s} = B_s - ME_s$$

- If $DB_{0,s} \ge 0$: Scenario is **FEASIBLE**. Spendable tourism budget $= DB_{0,s} - \text{Reserve}_s$ (5% contingency).
- If $DB_{0,s} < 0$: Scenario is marked **OVER_BUDGET** with $\text{Shortfall}_s = |DB_{0,s}|$. Standard leisure recommendations are held until budget parameters are adjusted.

### 3. Dynamic Package Inclusion Credit ($EPC_p$)
When an agency package includes services already accounted for in the scenario's mandatory expenditures:
$$\text{Credit}_{p,c} = \min(B_c, V_{p,c})$$
$$I_p = \sum_{c} \text{Credit}_{p,c}$$
$$EPC_p = P_p - I_p$$
$$R_p = DB_{0,s} - EPC_p$$

- **Double-Counting Protection**: Credits are strictly capped at the budgeted category line item ($B_c$).
- **Proration**: Unused nights or fractional party sizes are prorated. Non-budgeted services (sightseeing, museum passes, meals) receive zero credit against mandatory costs.

### 4. Multi-Criteria Decision Making (MCDM) Ranking Scores

- **Hospital Match Score ($HScore$)**:
  $$HScore = 0.45T + 0.20C + 0.15I + 0.10G + 0.10V$$
  *(Treatment match $T$, Cost suitability $C$, International patient services $I$, Geographic connectivity $G$, Verification confidence $V$)*

- **Tourism Destination Score ($DScore$)**:
  $$DScore(d) = 0.40 I_s + 0.25 G_s + 0.20 C_s + 0.15 V_s$$
  *(Interest category match $I_s$, Proximity/Transit score $G_s$, Cost suitability $C_s$, Verification $V_s$)*

- **Agency Package Ranking Score ($PScore$)**:
  $$PScore(p) = 0.45\text{Coverage} + 0.20\text{CostEff} + 0.20\text{ItineraryFit} + 0.10\text{ServiceComp} + 0.05\text{AgencyConf}$$

---

## Repository Structure

```text
TourPlus/
├── backend/                       # Django 5.2 LTS backend monolith
│   ├── apps/                      # Modular domain applications
│   │   ├── accounts/              # Custom UUID User, PatientProfile, Consents
│   │   ├── geography/             # Countries, States, Cities, ExchangeRates
│   │   ├── medical/               # Specialties, TreatmentCategories
│   │   ├── hospitals/             # Hospitals, Offerings, CostEstimates
│   │   ├── tourism/               # Destinations, Categories, Travel Limits
│   │   ├── agencies/              # Curated Travel Agencies
│   │   ├── packages/              # TravelPackages, Inclusions, Destinations
│   │   ├── trip_planning/         # TripRequests, Interests, Preferences
│   │   ├── recommendations/       # RecommendationRuns, Scenarios, BudgetLines, Matches
│   │   ├── final_plans/           # FinalPlans, Itineraries, Exports
│   │   └── audit/                 # AuditEvents, System Configurations
│   ├── engines/                   # Core deterministic calculation engines
│   │   ├── hospitals/             # Hard filtering & MCDM ranking engine
│   │   ├── budgeting/             # Decimal ledger, ranges, shortfall detection
│   │   ├── tourism/               # 3-tier scope classifier & recovery boundary
│   │   └── package_matching/      # Package coverage & Dynamic Inclusion Credit
│   ├── integrations/              # External service adapters
│   │   ├── maps/                  # Route engine with Haversine fallback
│   │   ├── exchange_rates/        # Multi-currency converter
│   │   └── llm/                   # Gemini/OpenAI adapter with fallback
│   ├── common/                    # Shared permissions, pagination, validators
│   ├── config/                    # Django configuration (base, dev, prod)
│   └── tests/                     # Automated unit, integration, and E2E tests
├── frontend/                      # Next.js 15 App Router web client
│   ├── src/app/                   # App Router pages and layouts
│   │   ├── (public)/              # Landing (/), How it works, About
│   │   ├── (auth)/                # Login, Register
│   │   └── (patient)/             # Dashboard, Wizard, Scenarios, Final Plan
│   ├── src/components/            # UI primitives (buttons, cards, badges, alerts)
│   ├── src/lib/                   # API client, Supabase client, currency helpers
│   └── src/types/                 # Centralized TypeScript definitions
├── docs/                          # Comprehensive technical documentation & ADRs
│   ├── architecture.md            # System architecture and design patterns
│   ├── database-schema.md         # Entity-relationship diagrams and table specs
│   ├── api-contracts.md           # REST endpoint request/response specifications
│   ├── recommendation-methodology.md # MCDM scoring and 3-tier hierarchy
│   ├── financial-model.md         # Exact Decimal financial ledger mathematics
│   ├── security-and-privacy.md    # Authentication, permissions, and PHI policy
│   └── decisions/                 # ADR-001, ADR-002, ADR-003
├── scripts/                       # Operational and validation scripts
│   ├── seed_demo_data.py          # Seed curated database catalogue
│   └── validate_catalogue.py      # Verify database integrity and invariants
├── .env.example                   # Environment configuration template
├── docker-compose.yml             # Local PostgreSQL 16 + PostGIS service
├── PRODUCT.md                     # Product requirements and source of truth
└── implementation_plan.md         # Phase-by-phase execution plan and checklist
```

---

## Quickstart Guide

### Prerequisites
- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher
- **Package Manager**: `pnpm` (recommended) or `npm`
- **Database**: Supabase PostgreSQL instance (or local PostgreSQL / SQLite)

---

### 1. Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Create and activate a Python virtual environment
python -m venv .venv
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements/dev.txt

# Run database migrations
python manage.py migrate

# Seed the curated medical and tourism catalogue
python manage.py seed_catalogue

# Start the Django development server
python manage.py runserver
```

The Django REST API will be available at: **`http://localhost:8000/api/v1/`**  
Django Admin dashboard: **`http://localhost:8000/admin/`**

---

### 2. Frontend Setup

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies using pnpm
pnpm install

# Start the Next.js development server
pnpm run dev
```

The web client will be running at: **`http://localhost:3000/`**

---

## Database & Supabase Integration

TourPlus AI natively supports **Supabase (PostgreSQL + PostGIS)**.

### Connecting to Supabase

1. Copy `.env.example` to `.env.local`:
   ```bash
   cp .env.example .env.local
   ```
2. Retrieve your credentials from the **Supabase Dashboard**:
   - **API Credentials** (`Settings -> API`):
     - `NEXT_PUBLIC_SUPABASE_URL`
     - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - **Database Connection String** (`Settings -> Database -> Connection string: URI`):
     - For connection pooling (Transaction mode `port 6543` / Session mode `port 5432`):
       ```text
       DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require
       ```
     - Or direct connection:
       ```text
       DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres?sslmode=require
       ```

> **Zero-Config Local Fallback**: If `DATABASE_URL` is omitted, Django automatically configures local SQLite (`db.sqlite3`), allowing instant offline development and testing.

---

## API Contracts

All endpoints are versioned under `/api/v1/`.

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/v1/health/` | Service health status | No |
| `POST` | `/api/v1/auth/register/` | Register a new patient account | No |
| `POST` | `/api/v1/auth/login/` | Patient authentication & JWT/session | No |
| `POST` | `/api/v1/auth/logout/` | Terminate session | Yes |
| `GET` | `/api/v1/auth/me/` | Current user profile | Yes |
| `GET` | `/api/v1/catalog/specialties/` | List medical specialties | No |
| `GET` | `/api/v1/catalog/treatment-categories/` | List treatment procedures | No |
| `GET` | `/api/v1/catalog/cities/` | List hospital cities | No |
| `GET` | `/api/v1/hospitals/` | List published hospitals | No |
| `GET` | `/api/v1/destinations/` | List tourist destinations | No |
| `POST` | `/api/v1/trip-requests/` | Create intake request draft | Yes |
| `PATCH` | `/api/v1/trip-requests/{id}/` | Autosave assessment wizard | Yes |
| `POST` | `/api/v1/trip-requests/{id}/generate-plan/` | Trigger 4-engine recommendation run | Yes |
| `GET` | `/api/v1/recommendations/runs/` | List past recommendation runs | Yes |
| `GET` | `/api/v1/recommendations/scenarios/{id}/` | Hospital scenario with budget lines | Yes |
| `GET` | `/api/v1/recommendations/scenarios/{id}/destinations/` | 3-tier recommended destinations | Yes |
| `GET` | `/api/v1/recommendations/scenarios/{id}/packages/` | Matched packages & inclusion credits | Yes |
| `POST` | `/api/v1/final-plans/` | Save final selected medical-tourism plan | Yes |
| `GET` | `/api/v1/final-plans/{id}/` | Retrieve saved final plan | Yes |
| `GET` | `/api/v1/final-plans/{id}/export/` | Render printable itinerary export | Yes |

---

## Automated Testing & Verification

### 1. Backend Test Suite
```bash
cd backend
python manage.py test tests
```
*Executes all 15 automated test suites: authentication, catalogue views, MCDM hospital ranking engine, Decimal budget ledger, 3-tier tourism engine, package inclusion credit math, and complete end-to-end planning journeys.*

### 2. Catalogue Integrity Validator
```bash
python scripts/validate_catalogue.py
```
*Verifies database invariants across countries, hospital offerings, tourist destinations, agency packages, and exchange rates.*

### 3. Code Linting & Type Checking
```bash
cd backend
flake8 backend --exclude=backend/.venv --select=F401,F821,E999
```

### 4. Next.js Production Build
```bash
cd frontend
pnpm run build
```
*Verifies compilation, TypeScript type checking, and static generation across all 11 routes.*

---

## Security & Privacy Policy

- **UUID Primary Keys**: Non-sequential UUIDv4 primary keys prevent resource enumeration.
- **Strict Object-Level Permissions**: Patient A cannot access Patient B's requests, scenarios, or final plans (`IsOwner`).
- **Data Minimization**: The platform does **not** ingest or store raw patient diagnostic charts, imaging files (DICOM/X-ray), or identifiable health records.
- **Password Security**: Passwords are encrypted with PBKDF2 using a SHA-256 hash.

---

## Medical & Financial Disclaimers

> **IMPORTANT MEDICAL NOTICE**: TourPlus AI provides non-clinical administrative, logistical, and financial decision support only. It is **not** a licensed healthcare provider, medical clinic, or hospital. The platform does **not** provide diagnoses, treatment prescriptions, or clinical triage. All surgical procedures, clinical recovery schedules, mobility limitations, and travel feasibility clearances must be evaluated and approved by the patient's licensed treating physician.

> **FINANCIAL ESTIMATE NOTICE**: All displayed medical treatment costs, accommodation rates, and flight costs are indicative estimates based on curated hospital offerings. Final hospital billing depends on diagnostic evaluation upon arrival, surgical complexity, and required clinical length of stay.

---

## License

Proprietary © 2026 TourPlus AI. All rights reserved.
