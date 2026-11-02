# ADR-001: Modular Monolith Architecture

## Status
Accepted

## Context
TourPlus AI connects multiple interrelated domains: medical offerings, multi-currency budgeting, tourism catalog, travel agency packages, and dynamic scenario matching. An early microservice architecture would introduce distributed transactions, deployment complexity, latency, and integration friction for a v1 MVP.

## Decision
We implement a **Modular Monolith** using Django 5.2 LTS and Django REST Framework for the backend:
- Domain boundaries are strictly enforced via Django apps (`accounts`, `geography`, `medical`, `hospitals`, `tourism`, `agencies`, `packages`, `trip_planning`, `recommendations`, `final_plans`, `audit`).
- Complex mathematical and optimization rules are isolated in `backend/engines/` rather than mixed inside views or model methods.
- Third-party services (LLMs, Maps, Exchange Rates) are isolated behind provider adapters in `backend/integrations/`.
- Frontend is a unified Next.js 15 App Router application with feature-sliced organization.

## Consequences
- **Positive:** Single deployment target, unified relational integrity in PostgreSQL/PostGIS, ACID transactions for recommendation runs, shared typing, and rapid development.
- **Negative:** Must maintain discipline to prevent circular imports between Django apps; engines must remain pure and decouple calculation logic from database queries where feasible.

