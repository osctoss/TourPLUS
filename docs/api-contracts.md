# API Contracts Specification — TourPlus AI

Base URL: `/api/v1/`

## 1. Authentication Endpoints

- `POST /api/v1/auth/register/`: Register a new patient account.
- `POST /api/v1/auth/login/`: Authenticate and receive session/auth tokens.
- `POST /api/v1/auth/logout/`: Terminate user session.
- `GET /api/v1/auth/me/`: Retrieve current user profile.

## 2. Public Catalogue Endpoints

- `GET /api/v1/catalog/specialties/`: List active medical specialties.
- `GET /api/v1/catalog/treatment-categories/`: List treatment categories (supports `?specialty=<slug>`).
- `GET /api/v1/catalog/cities/`: List active hospital cities.
- `GET /api/v1/hospitals/`: List published hospitals with international patient support.
- `GET /api/v1/destinations/`: List published tourist destinations with intensity ratings.

## 3. Trip Planning & Orchestration

- `POST /api/v1/trip-requests/`: Create or draft a new patient assessment request.
- `GET /api/v1/trip-requests/{id}/`: Retrieve request details.
- `PATCH /api/v1/trip-requests/{id}/`: Update/autosave assessment wizard draft.
- `POST /api/v1/trip-requests/{id}/generate-plan/`: Execute recommendation run across all 4 deterministic engines.

## 4. Recommendation Scenarios

- `GET /api/v1/recommendations/runs/?trip_request={id}`: List runs for request.
- `GET /api/v1/recommendations/scenarios/{id}/`: Retrieve specific hospital scenario with budget lines.
- `GET /api/v1/recommendations/scenarios/{id}/destinations/?scope={scope}`: Filter recommended attractions by scope (`LOCAL_REGIONAL`, `STATE_LEVEL`, `NATIONAL`).
- `GET /api/v1/recommendations/scenarios/{id}/packages/`: List matched packages with inclusion credits and effective costs.

## 5. Final Plans

- `POST /api/v1/final-plans/`: Persist patient's selected hospital scenario, chosen package, and destination sequence.
- `GET /api/v1/final-plans/{id}/`: Retrieve full final plan.
- `GET /api/v1/final-plans/{id}/export/`: Render printable export payload.

