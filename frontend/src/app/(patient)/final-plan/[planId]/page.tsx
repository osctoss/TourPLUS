"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiClient } from "@/lib/api-client";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { MedicalSafetyDisclaimer, FinancialSafetyDisclaimer } from "@/components/feedback/disclaimer";

export default function FinalPlanDetailPage() {
  const params = useParams();
  const planId = params.planId as string;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exportData, setExportData] = useState<any>(null);

  useEffect(() => {
    async function loadPlan() {
      try {
        setLoading(true);
        const data = await apiClient.get<any>(`/final-plans/${planId}/export/`);
        setExportData(data);
      } catch (err: any) {
        setError(err.message || "Failed to load final plan details.");
      } finally {
        setLoading(false);
      }
    }
    if (planId) {
      loadPlan();
    }
  }, [planId]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-brand-blue border-r-transparent mb-4" />
        <h2 className="text-xl font-bold text-slate-800">Generating Comprehensive Final Plan Document...</h2>
      </div>
    );
  }

  if (error || !exportData) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <Alert variant="danger" title="Plan Not Found">
          {error || "Could not retrieve the requested final plan."}
        </Alert>
        <div className="mt-6">
          <Link href="/dashboard">
            <Button variant="outline">Back to Dashboard</Button>
          </Link>
        </div>
      </div>
    );
  }

  const { hospital, financial_ledger, tourism_itinerary, disclaimers, patient } = exportData;

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Action Header (Hidden in Print) */}
      <div className="flex justify-between items-center mb-6 print:hidden">
        <Link href="/dashboard">
          <Button variant="outline" size="sm">
            &larr; Back to Dashboard
          </Button>
        </Link>
        <div className="flex gap-3">
          <Button onClick={handlePrint} className="bg-brand-blue text-white hover:bg-brand-primary">
            Print / Save as PDF
          </Button>
        </div>
      </div>

      {/* Official Plan Document Container */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 sm:p-10 space-y-8 print:border-none print:shadow-none print:p-0">
        {/* Document Header */}
        <div className="border-b border-slate-200 pb-6 flex flex-col sm:flex-row justify-between items-start gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-brand-blue">
                TourPlus AI Medical Tourism Itinerary
              </span>
              <Badge variant="success">Confirmed Plan</Badge>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900">{exportData.plan_title}</h1>
            <p className="text-xs text-slate-500 mt-1">
              Plan Ref: {exportData.plan_id} &bull; Created: {new Date(exportData.created_at).toLocaleDateString()} &bull;
              Patient: {patient.full_name} ({patient.email})
            </p>
          </div>
          <div className="text-right sm:self-center">
            <span className="text-xs text-slate-400 block uppercase">Total Estimated Commitment</span>
            <span className="text-2xl font-bold text-brand-primary font-mono">
              {financial_ledger.currency}{" "}
              {parseFloat(financial_ledger.total_estimated_commitment).toLocaleString(undefined, {
                minimumFractionDigits: 2,
              })}
            </span>
          </div>
        </div>

        {/* Section 1: Clinical Healthcare Facility */}
        <div>
          <h2 className="text-base font-bold text-slate-800 uppercase tracking-wider mb-3">
            1. Matched Healthcare Facility
          </h2>
          <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 text-sm">
            <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2 mb-2">
              <span className="font-bold text-slate-900 text-base">{hospital.name}</span>
              <div className="flex gap-2">
                <Badge variant="success">{hospital.verification_status}</Badge>
                {hospital.international_patient_support && (
                  <Badge variant="outline">International Patient Desk</Badge>
                )}
              </div>
            </div>
            <p className="text-xs text-slate-600 mb-2">
              {hospital.address ? `${hospital.address}, ` : ""}
              {hospital.city}, India
            </p>
            <div className="pt-2 border-t border-slate-200 text-xs text-slate-700">
              <span className="font-semibold">Verified Clinical Procedure:</span>{" "}
              {hospital.treatment_offering.category} ({hospital.treatment_offering.specialty})
            </div>
          </div>
        </div>

        {/* Section 2: Financial Ledger & Inclusions */}
        <div>
          <h2 className="text-base font-bold text-slate-800 uppercase tracking-wider mb-3">
            2. Itemized Financial Ledger & Inclusion Credits
          </h2>
          <div className="overflow-x-auto border border-slate-200 rounded-lg">
            <table className="w-full text-left text-xs sm:text-sm">
              <thead className="bg-slate-50 border-b border-slate-200 text-xs text-slate-500 uppercase">
                <tr>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Description</th>
                  <th className="py-2.5 px-3 text-right">Amount ({financial_ledger.currency})</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {financial_ledger.budget_lines.map((line: any, idx: number) => (
                  <tr key={idx}>
                    <td className="py-2 px-3 font-medium text-slate-800">{line.category_label}</td>
                    <td className="py-2 px-3 text-slate-600 text-xs">{line.description}</td>
                    <td className="py-2 px-3 text-right font-mono font-medium text-slate-900">
                      {parseFloat(line.expected_amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </td>
                  </tr>
                ))}
                <tr className="bg-slate-50 font-bold border-t border-slate-200">
                  <td colSpan={2} className="py-2.5 px-3 text-slate-800">
                    Mandatory Hospital & Travel Baseline Total
                  </td>
                  <td className="py-2.5 px-3 text-right font-mono text-slate-900">
                    {parseFloat(financial_ledger.mandatory_expenditure).toLocaleString(undefined, {
                      minimumFractionDigits: 2,
                    })}
                  </td>
                </tr>

                {parseFloat(financial_ledger.package_effective_incremental_cost) > 0 && (
                  <>
                    <tr>
                      <td className="py-2 px-3 font-medium text-slate-800">Travel Package Add-on</td>
                      <td className="py-2 px-3 text-slate-600 text-xs">
                        Listed Price ({financial_ledger.currency} {parseFloat(financial_ledger.package_listed_price).toFixed(2)}) minus
                        Dynamic Inclusion Credit (-{financial_ledger.currency} {parseFloat(financial_ledger.package_inclusion_credit).toFixed(2)})
                      </td>
                      <td className="py-2 px-3 text-right font-mono font-medium text-brand-green">
                        +{parseFloat(financial_ledger.package_effective_incremental_cost).toLocaleString(undefined, {
                          minimumFractionDigits: 2,
                        })}
                      </td>
                    </tr>
                    <tr className="bg-blue-50 font-bold border-t border-blue-200">
                      <td colSpan={2} className="py-3 px-3 text-brand-primary">
                        Total Estimated Financial Commitment
                      </td>
                      <td className="py-3 px-3 text-right font-mono text-base text-brand-primary">
                        {parseFloat(financial_ledger.total_estimated_commitment).toLocaleString(undefined, {
                          minimumFractionDigits: 2,
                        })}
                      </td>
                    </tr>
                  </>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Section 3: Recovery Tourism Itinerary */}
        <div>
          <h2 className="text-base font-bold text-slate-800 uppercase tracking-wider mb-3">
            3. Recovery Tourism Itinerary
          </h2>
          {tourism_itinerary.length === 0 ? (
            <p className="text-xs text-slate-500 italic">No leisure tourist stops selected for this plan.</p>
          ) : (
            <div className="space-y-3">
              {tourism_itinerary.map((stop: any) => (
                <div
                  key={stop.sequence_order}
                  className="flex items-center justify-between p-3 bg-slate-50 border border-slate-200 rounded-lg text-sm"
                >
                  <div className="flex items-center gap-3">
                    <span className="flex items-center justify-center h-6 w-6 rounded-full bg-brand-primary text-white text-xs font-bold">
                      {stop.sequence_order}
                    </span>
                    <div>
                      <span className="font-bold text-slate-900">{stop.destination_name}</span>
                      <span className="text-xs text-slate-500 block">
                        {stop.city} &bull; Suggested duration: {stop.planned_duration_minutes} mins
                      </span>
                    </div>
                  </div>
                  <Badge variant="default">{stop.travel_intensity} Intensity</Badge>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Mandatory Clinical & Financial Disclaimers */}
        <div className="space-y-4 pt-4 border-t border-slate-200">
          <MedicalSafetyDisclaimer />
          <FinancialSafetyDisclaimer />
        </div>
      </div>
    </div>
  );
}
