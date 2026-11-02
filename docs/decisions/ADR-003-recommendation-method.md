# ADR-003: Two-Stage Recommendation Architecture with Recovery Guardrails

## Status
Accepted

## Context
Medical tourism planning requires medical safety above all else. Recommendation algorithms must not recommend strenuous tourism activities or distant travel to patients undergoing intense medical procedures, regardless of patient preference or attractive pricing. Additionally, AI/LLMs must not hallucinate medical suitability or prices.

## Decision
1. **Two-Stage Architecture**:
   - **Stage 1: Hard Constraints (Filtering)**: Ineligible hospitals (unverified offering, missing data, outside specialty) and infeasible tourism destinations (violating recovery constraints, outside travel window, over budget) are completely excluded.
   - **Stage 2: Multi-Criteria Soft Ranking (MCDM)**: Weighted linear combination scoring evaluates only the feasible survivors.
2. **Deterministic Engine with LLM as Optional Layer**:
   - The core recommendation engine is 100% deterministic Python code.
   - The LLM is restricted to: (a) extracting structured requirements from unstructured doctor notes/patient text, and (b) generating natural language summaries of computed results.
   - If the LLM provider fails, system falls back to rule-based templated explanations without breaking the flow.

## Consequences
- Guaranteed medical safety boundaries.
- Resilient operation even during LLM API outages or rate limits.

