# Recommendation Methodology — TourPlus AI

## 1. Hospital Eligibility & Ranking

### Hard Filters
A hospital must satisfy:
1. Active record in verified city.
2. Verified treatment offering matching patient's requested specialty and procedure.
3. Published data status.

### Multi-Criteria Decision Making (MCDM) Score
$$HScore = 0.45T + 0.20C + 0.15I + 0.10G + 0.10V$$

- $T$: Treatment capability and offering verification.
- $C$: Cost suitability relative to budget range.
- $I$: Dedicated international patient support (visa, interpreters, transfer).
- $G$: Geographic connectivity and accessibility.
- $V$: Clinical data verification status (`VERIFIED` = 1.0, `INDICATIVE` = 0.8).

---

## 2. Recovery-Aware 3-Tier Tourism Engine

### Scope Classification relative to Hospital City
1. **`LOCAL_REGIONAL`**: Within 100 km or 2 hours transit time.
2. **`STATE_LEVEL`**: Within the same Indian state or up to 350 km.
3. **`NATIONAL`**: Pan-India travel requiring inter-state rail/flight.

### Clinical Safety Boundary
- If patient's `clinician_travel_guidance_status == NOT_PROVIDED`, all sightseeing is marked `REQUIRES_CLINICAL_REVIEW`.
- High physical intensity destinations are flagged if the patient requests low travel demand.

### Composite Destination Score
$$DScore(d) = 0.40 I_s + 0.25 G_s + 0.20 C_s + 0.15 V_s$$

- $I_s$: Category interest match with user weights (1–5).
- $G_s$: Proximity and transit duration score.
- $C_s$: Entry and transit cost suitability.
- $V_s$: Verification confidence.
