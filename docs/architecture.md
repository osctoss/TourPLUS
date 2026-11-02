# Architecture Overview — TourPlus AI

## 1. Modular Monolith Architecture

TourPlus AI follows a **modular monolith** pattern with a strict separation between domain data models, deterministic calculation engines, and presentation layers.

```mermaid
flowchart TD
    subgraph FrontendClient ["Next.js 15 Client (App Router)"]
        Wizard["Assessment Wizard"]
        HospitalDash["Hospital Scenarios"]
        BudgetLedger["Budget Ledger UI"]
        TourismUI["3-Tier Tourism"]
        PackageUI["Package Credits"]
        FinalPlanUI["Final Plan Synthesis"]
    end

    subgraph DjangoBackend ["Django 5.2 LTS Monolith"]
        Gateway["REST API Gateway (/api/v1/)"]
        AuthModule["apps.accounts"]
        PlanningModule["apps.trip_planning"]
        RecModule["apps.recommendations"]
        FinalPlanModule["apps.final_plans"]

        subgraph CoreEngines ["Deterministic Core Engines"]
            HospitalEngine["engines.hospitals (MCDM)"]
            BudgetEngine["engines.budgeting (Decimal)"]
            TourismEngine["engines.tourism (3-Tier)"]
            PackageEngine["engines.package_matching (Credit)"]
        end

        subgraph Integrations ["Integration Adapters"]
            FXAdapter["integrations.exchange_rates"]
            MapsAdapter["integrations.maps"]
            LLMAdapter["integrations.llm"]
        end
    end

    subgraph Persistence ["PostgreSQL / PostGIS"]
        DB[(System of Record)]
    end

    FrontendClient <-->|HTTPS / JSON / JWT| Gateway
    Gateway --> AuthModule & PlanningModule & RecModule & FinalPlanModule
    RecModule --> HospitalEngine & BudgetEngine & TourismEngine & PackageEngine
    HospitalEngine & BudgetEngine & TourismEngine & PackageEngine --> DB
    TourismEngine --> MapsAdapter
    BudgetEngine --> FXAdapter
    RecModule --> LLMAdapter
```

## 2. Key Design Decisions

1. **Deterministic Engines**: Financial calculations and recommendation scores are computed using pure mathematical formulas and Python `Decimal` arithmetic.
2. **Hospital-Specific Scenarios**: Because treatment costs, lodging, flights, and travel feasibility vary by hospital and destination city, the system generates separate, parallel scenarios for each eligible hospital.
3. **Double-Counting Prevention**: When travel agencies offer packages that include flights or hotel nights, the system credits those against the mandatory budget ledger, showing the true effective incremental cost.
4. **Data Provenance**: Every entity is explicitly classified as `VERIFIED`, `INDICATIVE`, or `DEMO` to maintain trust with patients.

