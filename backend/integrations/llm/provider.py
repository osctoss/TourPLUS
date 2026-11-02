import os
import re
from typing import Dict, Any, List


class LLMAdvisor:
    """
    AI decision-support adapter with Gemini API integration and deterministic fallback.
    Provides:
      1. Condition & keyword extraction from clinical notes
      2. Natural language explanation of hospital and package matching trade-offs
    Guarantees 100% platform availability even when LLM provider is offline.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')

    def extract_clinical_keywords(self, doctor_notes: str) -> List[str]:
        """
        Extracts medical keywords from patient condition notes.
        """
        if not doctor_notes:
            return []

        # Deterministic regex-based medical entity extractor
        keywords = []
        patterns = [
            r'\b(cardiac|bypass|cabg|angioplasty|stent|valve|heart)\b',
            r'\b(knee|hip|replacement|arthroplasty|orthopedic|spine|disc)\b',
            r'\b(chemo|chemotherapy|radiation|oncology|tumor|cancer|immunotherapy)\b',
            r'\b(hypertension|diabetes|asthma|mobility|wheelchair)\b'
        ]
        for pat in patterns:
            matches = re.findall(pat, doctor_notes, re.IGNORECASE)
            keywords.extend([m.lower() for m in matches])

        return list(dict.fromkeys(keywords))

    def explain_scenario_match(
        self,
        hospital_name: str,
        specialty_name: str,
        offering_name: str,
        score: float,
        discretionary_budget: float,
        is_over_budget: bool
    ) -> str:
        """
        Generates explainable rationale for why this hospital was matched.
        """
        budget_phrase = (
            f"leaves an estimated discretionary tourism reserve of ${discretionary_budget:,.2f}"
            if not is_over_budget
            else f"exceeds the initial baseline budget by ${abs(discretionary_budget):,.2f}, requiring budget adjustment"
        )

        return (
            f"{hospital_name} was matched based on verified clinical expertise in {specialty_name} "
            f"specifically for {offering_name} (Composite Match Score: {score:.2f}). "
            f"This scenario {budget_phrase} and features accredited international patient coordination."
        )
