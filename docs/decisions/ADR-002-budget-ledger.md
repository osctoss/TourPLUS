# ADR-002: Deterministic Budget Ledger & Inclusion Credit Calculation

## Status
Accepted

## Context
Standard travel sites quote total package prices or display opaque cost estimates. In medical tourism, patients commit significant capital for treatment, flights, accommodation, visas, and local logistics before considering tourism. When booking agency tour packages, packages often include accommodation or local transport that the patient already accounted for in their mandatory hospital stay budget. Counting both results in double-charging the patient in their planning budget.

## Decision
1. **Scenario-Specific Budget Ledger**: Every hospital generates its own discrete budget scenario with itemized lines (`scenario_budget_lines`) using Python `Decimal` with fixed 2-decimal precision.
2. **Recorded FX Snapshots**: Conversions from source currencies to scenario currencies record the exact rate snapshot used at runtime.
3. **Dynamic Package Inclusion Credit**:
   $$\text{Credit}_{p,c} = \min(B_c, V_{p,c}), \quad I_p = \sum_c \text{Credit}_{p,c}$$
   $$EPC_p = P_p - I_p$$
4. **Explicit Junction Ledger**: Each applied credit is recorded in `package_match_inclusion_credits` with the specific `package_inclusion_id`, `scenario_budget_line_id`, and proration rationale. Speculative, unbudgeted, or unverified services receive 0 credit.

## Consequences
- Transparent, audit-proof financial reconciliation with zero floating-point drift.
- Clear user-facing explanation showing why a package effectively costs less than its sticker price.

