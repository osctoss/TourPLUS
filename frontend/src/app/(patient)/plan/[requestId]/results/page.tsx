"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { apiClient } from "@/lib/api-client";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { MedicalSafetyDisclaimer, FinancialSafetyDisclaimer } from "@/components/feedback/disclaimer";

export default function PlanResultsPage() {
  const params = useParams();
  const router = useRouter();
  const requestId = params.requestId as string;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tripRequest, setTripRequest] = useState<any>(null);
  const [run, setRun] = useState<any>(null);
  const [scenarios, setScenarios] = useState<any[]>([]);

  useEffect(() => {
    async function loadResults() {
      try {
        setLoading(true);
        // Load trip request details
        const trip = await apiClient.get<any>(`/trip-requests/${requestId}/`);
        setTripRequest(trip);

        // Load recommendation runs
        const runsRes = await apiClient.get<any>(`/recommendations/runs/?trip_request=${requestId}`);
        const runsList = runsRes.results || runsRes || [];
        if (runsList.length > 0) {
          const latestRun = runsList[0];
          setRun(latestRun);
          setScenarios(latestRun.scenarios || []);
        } else {
          setError("No recommendation runs found for this assessment request.");
        }
      } catch (err: any) {
        setError(err.message || "Failed to load recommendation results.");
      } finally {
        setLoading(false);
      }
    }
    if (requestId) {
      loadResults();
    }
  }, [requestId]);

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-16 text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-brand-blue border-r-transparent mb-4" />
        <h2 className="text-xl font-bold text-slate-800">Synthesizing Clinical & Tourism Scenarios...</h2>
        <p className="text-slate-500 text-sm mt-1">
          Evaluating verified offerings, calculating decimal budget ledgers, and matching dynamic packages.
        </p>
      </div>
    );
  }

  if (error || !tripRequest) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <Alert variant="danger" title="Unable to Load Scenarios">
          {error || "Assessment request not found."}
        </Alert>
        <div className="mt-6">
          <Link href="/plan/new">
            <Button variant="outline">Start New Assessment</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Assessment Header */}
      <div className="mb-8">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Badge variant="success">Completed</Badge>
              <span className="text-xs text-slate-500">Run #{run?.run_number || 1}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900">
              Matched Hospital Scenarios
            </h1>
            <p className="text-slate-600 text-sm mt-1">
              {tripRequest.specialty_name} &bull; {tripRequest.treatment_category_name || "Verified Treatment"} &bull;{" "}
              {tripRequest.budget_currency} {parseFloat(tripRequest.total_budget_amount).toLocaleString()} Total Budget &bull;{" "}
              {tripRequest.party_size} Traveler(s)
            </p>
          </div>
          <Link href="/plan/new">
            <Button variant="outline" size="sm">
              Adjust Parameters
            </Button>
          </Link>
        </div>
      </div>

      {/* Safety Notice */}
      <div className="mb-8">
        <MedicalSafetyDisclaimer />
      </div>

      {/* Scenarios Grid */}
      {scenarios.length === 0 ? (
        <Card className="p-8 text-center">
          <p className="text-slate-600">No accredited hospital offerings matched all hard constraints for this specialty.</p>
        </Card>
      ) : (
        <div className="space-y-6">
          <div className="text-sm font-semibold text-slate-700">
            {scenarios.length} Matched Healthcare Institution{scenarios.length > 1 ? "s" : ""} (Ranked by Multi-Criteria HScore)
          </div>

          <div className="grid grid-cols-1 gap-6">
            {scenarios.map((scenario) => {
              const offering = scenario.hospital_offering;
              const hospital = offering?.hospital;
              const costEst = offering?.cost_estimate;

              // Calculate ledger totals from scenario.budget_lines
              const budgetLines = scenario.budget_lines || [];
              const mandatoryTotal = budgetLines.reduce(
                (acc: number, line: any) => acc + parseFloat(line.converted_expected_amount || 0),
                0
              );
              const totalBudgetVal = parseFloat(tripRequest.total_budget_amount || 0);
              const discretionaryVal = totalBudgetVal - mandatoryTotal;
              const isOverBudget = discretionaryVal < 0;

              return (
                <Card key={scenario.id} className="overflow-hidden border-slate-200 hover:shadow-md transition-shadow">
                  <div className="p-6">
                    <div className="flex flex-col lg:flex-row justify-between lg:items-center gap-4 pb-6 border-b border-slate-100">
                      <div>
                        <div className="flex flex-wrap items-center gap-2 mb-2">
                          <span className="inline-flex items-center justify-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-brand-primary text-white">
                            Rank #{scenario.rank}
                          </span>
                          <Badge variant="info">HScore: {(parseFloat(scenario.ranking_score) * 100).toFixed(1)}%</Badge>
                          {hospital?.verification_status === "VERIFIED" && (
                            <Badge variant="success">Verified Offering</Badge>
                          )}
                          {hospital?.international_patient_support && (
                            <Badge variant="outline">Dedicated Intl Patient Desk</Badge>
                          )}
                        </div>
                        <h3 className="text-xl font-bold text-slate-900">{hospital?.name}</h3>
                        <p className="text-sm text-slate-500">
                          {hospital?.city?.name}, {hospital?.city?.state?.name}, India &bull;{" "}
                          <span className="text-slate-700 font-medium">{offering?.treatment_category?.name}</span>
                        </p>
                      </div>

                      <div className="flex sm:flex-col items-end justify-between sm:justify-center">
                        <span className="text-xs text-slate-500 uppercase tracking-wider">
                          Indicative Procedure Cost
                        </span>
                        <div className="text-xl font-bold text-brand-primary">
                          {costEst?.currency || "USD"} {parseFloat(costEst?.expected_amount || 0).toLocaleString()}
                        </div>
                        <span className="text-[11px] text-slate-400">
                          Range: {parseFloat(costEst?.min_amount || 0).toLocaleString()} -{" "}
                          {parseFloat(costEst?.max_amount || 0).toLocaleString()}
                        </span>
                      </div>
                    </div>

                    {/* Financial Ledger Snapshot */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 my-6 p-4 bg-slate-50 rounded-lg text-sm">
                      <div>
                        <span className="block text-xs text-slate-500">Mandatory Trip Expenses</span>
                        <span className="font-bold text-slate-800">
                          {scenario.scenario_currency} {mandatoryTotal.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </span>
                        <span className="block text-[11px] text-slate-400">Procedure, Flights, Stay, Visa</span>
                      </div>
                      <div>
                        <span className="block text-xs text-slate-500">Discretionary Tourism Reserve</span>
                        <span className={`font-bold ${isOverBudget ? "text-danger-500" : "text-brand-green"}`}>
                          {scenario.scenario_currency} {discretionaryVal.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </span>
                        <span className="block text-[11px] text-slate-400">Available for packages & leisure</span>
                      </div>
                      <div>
                        <span className="block text-xs text-slate-500">Budget Status</span>
                        <span className={`font-bold ${isOverBudget ? "text-danger-500" : "text-brand-green"}`}>
                          {isOverBudget ? "Over Budget (Shortfall)" : "Feasible Balance"}
                        </span>
                        <span className="block text-[11px] text-slate-400">Zero double-counting applied</span>
                      </div>
                    </div>

                    {/* Scenario Action */}
                    <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
                      <p className="text-xs text-slate-500 italic">
                        {scenario.scenario_notes || "Independent scenario evaluated based on multi-criteria clinical matching."}
                      </p>
                      <Link href={`/scenario/${scenario.id}`} className="w-full sm:w-auto">
                        <Button className="w-full sm:w-auto bg-brand-blue text-white hover:bg-brand-primary">
                          Explore Scenario & Packages &rarr;
                        </Button>
                      </Link>
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>
        </div>
      )}

      <div className="mt-12">
        <FinancialSafetyDisclaimer />
      </div>
    </div>
  );
}

