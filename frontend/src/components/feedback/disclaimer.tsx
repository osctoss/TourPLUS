import React from "react";
import { ShieldAlert, DollarSign } from "lucide-react";

export function MedicalSafetyDisclaimer() {
  return (
    <div className="bg-surface rounded-lg p-4 border border-border flex items-start gap-3 text-xs text-muted leading-relaxed">
      <ShieldAlert className="h-5 w-5 text-blue shrink-0 mt-0.5" />
      <div>
        <span className="font-semibold text-primary block mb-0.5">Medical Safety & Advisory Notice</span>
        TourPlus AI provides informational decision support for medical-tourism planning. It does not diagnose conditions, prescribe treatment or determine whether a patient is fit to travel. Hospital and treatment decisions must be confirmed with qualified healthcare professionals. Recovery and travel restrictions must be discussed with the treating clinician.
      </div>
    </div>
  );
}

export function FinancialSafetyDisclaimer() {
  return (
    <div className="bg-surface rounded-lg p-4 border border-border flex items-start gap-3 text-xs text-muted leading-relaxed">
      <DollarSign className="h-5 w-5 text-green shrink-0 mt-0.5" />
      <div>
        <span className="font-semibold text-primary block mb-0.5">Financial & Quote Transparency Notice</span>
        Prices and cost breakdowns are estimates unless explicitly identified as a confirmed provider quote. Actual costs may vary by patient, treatment, dates, exchange rates, availability, taxes, and service inclusions. Confirm all prices and package conditions with the provider before making a commitment.
      </div>
    </div>
  );
}

