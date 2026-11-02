# Changelog

All notable changes to the TourPlus AI platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-11-02

### Added
- **Phase 0: Project Foundation & Baseline**
  - Monorepo structure with `.editorconfig`, `.env.example`, `docker-compose.yml` (PostgreSQL 16 + PostGIS).
  - Django 5.2 LTS backend configuration with modular settings (`base.py`, `development.py`, `production.py`).
  - Custom `User` model with UUID primary keys and role-based permissions (`PATIENT`, `ADMIN`, `DATA_CURATOR`).
  - Next.js 15 App Router frontend with Tailwind CSS design tokens matching Clinical Blue (`#103044`) and India Green (`#259970`).
  - System health endpoint (`GET /api/v1/health/`).
- **Phase 1: Domain Data Architecture & Admin Curation**
  - Geography, Medical, Hospitals, Tourism, Agencies, and Packages models.
  - Idempotent seed CLI (`python manage.py seed_catalogue` and `scripts/seed_demo_data.py`).
  - Public catalogue endpoints (`/api/v1/catalog/`, `/api/v1/hospitals/`, `/api/v1/destinations/`).
  - Authentication flow (`/auth/register/`, `/auth/login/`, `/auth/logout/`, `/auth/me/`).
- **Phase 2: Patient Assessment Wizard & Hospital Scenarios**
  - 6-step guided intake wizard (`/plan/new`) with draft autosave.
  - Multi-criteria decision making (MCDM) hospital ranking engine ($HScore = 0.45T + 0.20C + 0.15I + 0.10G + 0.10V$).
  - Scenario generation orchestrator (`/trip-requests/{id}/generate-plan/`).
  - Hospital comparison view (`/plan/[requestId]/results`).
- **Phase 3: Deterministic Budget Ledger Engine**
  - Python `Decimal` budget engine with multi-currency FX snapshot conversions.
  - Mandatory expenditure calculations ($ME_s = TC_s + FC_s + HC_s + VC_s + LC_s + MC_s$).
  - Initial discretionary budget computation ($DB_{0,s} = B_s - ME_s$) and shortfall detection.
  - Scenario budget UI (`/scenario/[scenarioId]`) with cost distribution breakdown.
- **Phase 4: Recovery-Aware 3-Tier Tourism Engine**
  - Hierarchical destination recommendations: `LOCAL_REGIONAL`, `STATE_LEVEL`, and `NATIONAL`.
  - Geographic transit estimator with Haversine distance and speed heuristics.
  - Clinical recovery safety boundary enforcement (`REQUIRES_CLINICAL_REVIEW`).
- **Phase 5: Dynamic Package Matching & Inclusion Credit Ledger**
  - Curated travel agency package matcher with destination coverage scoring.
  - Dynamic Package Inclusion Credit ($EPC_p = P_p - I_p$) preventing double-counting.
  - Interactive credit derivation and comparison UI.
- **Phase 6: Final Plan Synthesis & Release**
  - Final plan creation and persistence (`/api/v1/final-plans/`).
  - Unified plan overview and `@media print` optimized export view (`/final-plan/[planId]`).
  - Deterministic fallback LLM provider abstraction for condition extraction and explanation.
  - Patient dashboard (`/dashboard`) for tracking past runs and saved plans.
  - Comprehensive automated test suite with 15 test cases passing.
