# Financial Model & Ledger Mathematics — TourPlus AI

## 1. Principles
All monetary accounting in TourPlus AI is executed using Python `Decimal` objects with exact two-place quantization (`0.01`). Floating-point arithmetic is strictly prohibited to avoid rounding errors.

## 2. Mandatory Expenditure ($ME_s$)
For each hospital scenario $s$:
$$ME_s = TC_s + FC_s + HC_s + VC_s + LC_s + MC_s$$

Where:
- $TC_s$: Medical treatment cost.
- $FC_s$: International return airfare ($FC_s = \text{FlightUnit} \times \text{PartySize}$).
- $HC_s$: Medical recovery lodging ($HC_s = \text{NightlyRate} \times \text{StayNights} \times \lceil\text{PartySize}/2\rceil$).
- $VC_s$: Medical visa and government fees.
- $LC_s$: Dedicated local hospital and airport transfers.
- $MC_s$: Contingency and pharmacy supplies.

## 3. Discretionary Budget & Shortfall
$$DB_{0,s} = B_s - ME_s$$

- If $DB_{0,s} \ge 0$: Scenario is feasible. Spendable tourism budget $= DB_{0,s} - \text{Reserve}_s$ (5% reserve).
- If $DB_{0,s} < 0$: Scenario is marked `OVER_BUDGET` with $\text{Shortfall}_s = |DB_{0,s}|$. Standard package recommendation is blocked until resolved.

## 4. Dynamic Package Inclusion Credit ($EPC_p$)
When an agency travel package includes services already accounted for in mandatory expenditures:
$$\text{Credit}_{p,c} = \min(B_c, V_{p,c})$$
$$I_p = \sum_{c} \text{Credit}_{p,c}$$
$$EPC_p = P_p - I_p$$

- Double-counting prevention: Credits are strictly capped at the budgeted category line item ($B_c$).
- Exclusions: Optional extras, sightseeing activities, and meals receive zero credit against mandatory costs.

