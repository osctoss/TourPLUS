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

export default function ScenarioWorkbenchPage() {
  const params = useParams();
  const router = useRouter();
  const scenarioId = params.scenarioId as string;

  const [activeTab, setActiveTab] = useState<"budget" | "tourism" | "packages" | "finalize">("budget");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [scenario, setScenario] = useState<any>(null);
  const [destinations, setDestinations] = useState<any[]>([]);
  const [packages, setPackages] = useState<any[]>([]);

  // User selections for final plan
  const [selectedPackageId, setSelectedPackageId] = useState<string | null>(null);
  const [selectedDestinationIds, setSelectedDestinationIds] = useState<string[]>([]);
  const [planTitle, setPlanTitle] = useState("My Medical Tourism Plan");
  const [savingPlan, setSavingPlan] = useState(false);

  // Tourism scope filter
  const [tourismScopeFilter, setTourismScopeFilter] = useState<string>("ALL");

  useEffect(() => {
    async function loadScenarioData() {
      try {
        setLoading(true);
        const [scenRes, destRes, pkgRes] = await Promise.all([
          apiClient.get<any>(`/recommendations/scenarios/${scenarioId}/`),
          apiClient.get<any>(`/recommendations/scenarios/${scenarioId}/destinations/`),
          apiClient.get<any>(`/recommendations/scenarios/${scenarioId}/packages/`),
        ]);

        setScenario(scenRes);
        const destList = destRes.results || destRes || [];
        const pkgList = pkgRes.results || pkgRes || [];
        setDestinations(destList);
        setPackages(pkgList);

        if (pkgList.length > 0) {
          setSelectedPackageId(pkgList[0].id);
        }
        if (destList.length > 0) {
          // Preselect top 2 local destinations
          setSelectedDestinationIds(destList.slice(0, 2).map((d: any) => d.destination.id));
        }
      } catch (err: any) {
        setError(err.message || "Failed to load scenario details.");
      } finally {
        setLoading(false);
      }
    }
    if (scenarioId) {
      loadScenarioData();
    }
  }, [scenarioId]);

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-16 text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-brand-blue border-r-transparent mb-4" />
        <h2 className="text-xl font-bold text-slate-800">Loading Financial & Tourism Scenario...</h2>
      </div>
    );
  }

  if (error || !scenario) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <Alert variant="danger" title="Scenario Error">
          {error || "Scenario not found."}
        </Alert>
        <div className="mt-6">
          <Button variant="outline" onClick={() => router.back()}>
            &larr; Go Back
          </Button>
        </div>
      </div>
    );
  }

  const hospital = scenario.hospital_offering?.hospital;
  const offering = scenario.hospital_offering;
  const budgetLines = scenario.budget_lines || [];

  const mandatoryTotal = budgetLines.reduce(
    (acc: number, line: any) => acc + parseFloat(line.converted_expected_amount || 0),
    0
  );

  const selectedPkg = packages.find((p) => p.id === selectedPackageId);
  const pkgEffectiveCost = selectedPkg ? parseFloat(selectedPkg.effective_incremental_cost || 0) : 0;
  const pkgCredit = selectedPkg ? parseFloat(selectedPkg.inclusion_credit || 0) : 0;

  const toggleDestination = (destId: string) => {
    setSelectedDestinationIds((prev) =>
      prev.includes(destId) ? prev.filter((id) => id !== destId) : [...prev, destId]
    );
  };

  const handleSaveFinalPlan = async () => {
    try {
      setSavingPlan(true);
      const destinationsInput = selectedDestinationIds.map((destId, idx) => ({
        destination: destId,
        sequence_order: idx + 1,
        planned_duration_minutes: 120,
        notes: "Curated recovery tour stop",
      }));

      const plan = await apiClient.post<any>("/final-plans/", {
        hospital_scenario: scenario.id,
        package_match: selectedPackageId || undefined,
        plan_title: planTitle,
        selected_scope: "LOCAL_REGIONAL",
        destinations_input: destinationsInput,
      });

      router.push(`/final-plan/${plan.id}`);
    } catch (err: any) {
      setError(err.message || "Failed to save final plan.");
      setSavingPlan(false);
    }
  };

  const filteredDestinations = destinations.filter((d) => {
    if (tourismScopeFilter === "ALL") return true;
    return d.tourism_scope === tourismScopeFilter;
  });

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Scenario Header */}
      <div className="mb-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-brand-primary text-white">
                Rank #{scenario.rank}
              </span>
              <Badge variant="info">HScore: {(parseFloat(scenario.ranking_score) * 100).toFixed(1)}%</Badge>
              <Badge variant="success">Verified Offering</Badge>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900">{hospital?.name}</h1>
            <p className="text-sm text-slate-600">
              {hospital?.city?.name}, India &bull; {offering?.treatment_category?.name} ({offering?.treatment_category?.specialty_name || "Specialty"})
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => router.back()}>
              Back to Scenarios
            </Button>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-200 mb-8 overflow-x-auto">
        {[
          { key: "budget", label: "1. Budget Ledger" },
          { key: "tourism", label: "2. Recovery Tourism" },
          { key: "packages", label: "3. Dynamic Packages" },
          { key: "finalize", label: "4. Finalize Plan" },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`py-3 px-5 text-sm font-semibold border-b-2 whitespace-nowrap transition-colors ${
              activeTab === tab.key
                ? "border-brand-blue text-brand-blue"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* TAB 1: BUDGET LEDGER */}
      {activeTab === "budget" && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Mandatory Scenario Budget Ledger</CardTitle>
              <CardDescription>
                Deterministic Decimal accounting for all mandatory treatment, lodging, flight, and visa expenditures.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-slate-200 text-xs text-slate-500 uppercase">
                      <th className="py-3 px-4">Expense Category</th>
                      <th className="py-3 px-4">Description</th>
                      <th className="py-3 px-4 text-center">Classification</th>
                      <th className="py-3 px-4 text-right">Expected Amount</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {budgetLines.map((line: any) => (
                      <tr key={line.id} className="hover:bg-slate-50/50">
                        <td className="py-3 px-4 font-semibold text-slate-800">
                          {line.expense_category.replace(/_/g, " ")}
                        </td>
                        <td className="py-3 px-4 text-slate-600">{line.description}</td>
                        <td className="py-3 px-4 text-center">
                          <Badge variant={line.data_classification === "VERIFIED" ? "success" : "default"}>
                            {line.data_classification}
                          </Badge>
                        </td>
                        <td className="py-3 px-4 text-right font-mono font-semibold text-slate-900">
                          {line.scenario_currency}{" "}
                          {parseFloat(line.converted_expected_amount).toLocaleString(undefined, {
                            minimumFractionDigits: 2,
                          })}
                        </td>
                      </tr>
                    ))}
                    <tr className="bg-slate-50 font-bold border-t-2 border-slate-300">
                      <td colSpan={3} className="py-4 px-4 text-slate-900">
                        Total Mandatory Trip Expenditure
                      </td>
                      <td className="py-4 px-4 text-right text-base text-brand-primary">
                        {scenario.scenario_currency}{" "}
                        {mandatoryTotal.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-end">
            <Button onClick={() => setActiveTab("tourism")}>Next: Explore Recovery Tourism &rarr;</Button>
          </div>
        </div>
      )}

      {/* TAB 2: RECOVERY-AWARE TOURISM */}
      {activeTab === "tourism" && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h2 className="text-xl font-bold text-slate-900">Recovery-Aware Tourism Recommendations</h2>
              <p className="text-slate-500 text-sm">
                Destinations classified across 3 tiers (Local, State-Level, National) constrained by clinical recovery safety.
              </p>
            </div>
            {/* Scope Filter Buttons */}
            <div className="flex rounded-md shadow-sm bg-slate-100 p-1">
              {[
                { key: "ALL", label: "All" },
                { key: "LOCAL_REGIONAL", label: "Local / Regional" },
                { key: "STATE_LEVEL", label: "State-Level" },
                { key: "NATIONAL", label: "Pan-India" },
              ].map((scope) => (
                <button
                  key={scope.key}
                  onClick={() => setTourismScopeFilter(scope.key)}
                  className={`px-3 py-1.5 text-xs font-semibold rounded ${
                    tourismScopeFilter === scope.key
                      ? "bg-white text-slate-900 shadow-sm"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  {scope.label}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredDestinations.map((rec) => {
              const dest = rec.destination;
              const isSelected = selectedDestinationIds.includes(dest.id);
              const requiresClinical = rec.feasibility_status === "REQUIRES_CLINICAL_REVIEW";

              return (
                <Card
                  key={rec.id}
                  className={`border transition-all ${
                    isSelected ? "border-brand-blue ring-1 ring-brand-blue bg-blue-50/20" : "border-slate-200"
                  }`}
                >
                  <CardContent className="p-5">
                    <div className="flex justify-between items-start gap-3">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-bold uppercase tracking-wider text-brand-blue">
                            {rec.tourism_scope.replace(/_/g, " ")}
                          </span>
                          <span className="text-slate-300">&bull;</span>
                          <span className="text-xs text-slate-500">{dest.city?.name}</span>
                        </div>
                        <h4 className="text-lg font-bold text-slate-900">{dest.name}</h4>
                      </div>

                      <button
                        onClick={() => toggleDestination(dest.id)}
                        className={`text-xs px-3 py-1.5 rounded-full font-semibold transition-colors ${
                          isSelected
                            ? "bg-brand-blue text-white"
                            : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                        }`}
                      >
                        {isSelected ? "Selected" : "Add to Itinerary"}
                      </button>
                    </div>

                    <p className="text-xs text-slate-600 mt-2 line-clamp-2">{dest.description}</p>

                    <div className="grid grid-cols-2 gap-2 mt-4 pt-4 border-t border-slate-100 text-xs">
                      <div>
                        <span className="text-slate-400 block">Transit from Hospital</span>
                        <span className="font-semibold text-slate-700">~{rec.estimated_route_duration} mins</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block">Activity Intensity</span>
                        <span className="font-semibold text-slate-700">{dest.travel_intensity} Intensity</span>
                      </div>
                    </div>

                    {requiresClinical && (
                      <div className="mt-3 p-2 bg-amber-50 rounded border border-amber-200 text-[11px] text-amber-800 flex items-center gap-1.5">
                        <span>&#9888;</span>
                        <span>Requires confirmed clinical clearance by treating physician.</span>
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>

          <div className="flex justify-between items-center pt-4">
            <Button variant="outline" onClick={() => setActiveTab("budget")}>
              &larr; Back to Budget
            </Button>
            <Button onClick={() => setActiveTab("packages")}>Next: Match Travel Packages &rarr;</Button>
          </div>
        </div>
      )}

      {/* TAB 3: DYNAMIC TRAVEL PACKAGES */}
      {activeTab === "packages" && (
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-bold text-slate-900">Curated Travel Agency Packages</h2>
            <p className="text-slate-500 text-sm">
              Packages are matched against your destinations. Dynamic Inclusion Credits are deducted automatically to
              eliminate duplicate lodging and flight expenses.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {packages.map((pkgMatch) => {
              const pkg = pkgMatch.travel_package;
              const isSelected = selectedPackageId === pkgMatch.id;
              const creditVal = parseFloat(pkgMatch.inclusion_credit || 0);

              return (
                <Card
                  key={pkgMatch.id}
                  className={`border transition-all ${
                    isSelected ? "border-brand-green ring-2 ring-brand-green bg-green-50/10" : "border-slate-200"
                  }`}
                >
                  <CardHeader className="pb-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <Badge variant="outline">{pkg.agency?.name || "Verified Agency"}</Badge>
                        <CardTitle className="text-lg mt-2">{pkg.name}</CardTitle>
                      </div>
                      <Badge variant={pkgMatch.budget_feasibility_status === "FEASIBLE" ? "success" : "danger"}>
                        {pkgMatch.budget_feasibility_status === "FEASIBLE" ? "Within Budget" : "Exceeds Budget"}
                      </Badge>
                    </div>
                    <CardDescription>{pkg.duration_days} Days Curated Itinerary</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-xs text-slate-600 line-clamp-2">{pkg.description}</p>

                    {/* Financial Formula Breakdown */}
                    <div className="p-3 bg-slate-50 rounded-lg text-xs space-y-1.5 border border-slate-200">
                      <div className="flex justify-between text-slate-600">
                        <span>Listed Package Price (P_p):</span>
                        <span className="font-semibold text-slate-800">
                          {scenario.scenario_currency} {parseFloat(pkgMatch.listed_package_price).toLocaleString()}
                        </span>
                      </div>
                      <div className="flex justify-between text-brand-green font-medium">
                        <span>Dynamic Inclusion Credit (-I_p):</span>
                        <span>
                          -{scenario.scenario_currency} {creditVal.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </span>
                      </div>
                      <div className="flex justify-between border-t border-slate-200 pt-1.5 font-bold text-slate-900">
                        <span>Effective Incremental Cost (EPC_p):</span>
                        <span className="text-brand-primary">
                          {scenario.scenario_currency}{" "}
                          {parseFloat(pkgMatch.effective_incremental_cost).toLocaleString(undefined, {
                            minimumFractionDigits: 2,
                          })}
                        </span>
                      </div>
                    </div>

                    {/* Dynamic Credit Explanations */}
                    {pkgMatch.credits && pkgMatch.credits.length > 0 && (
                      <div className="text-[11px] text-slate-500 bg-blue-50/50 p-2.5 rounded border border-blue-100">
                        <span className="font-semibold text-brand-blue block mb-1">
                          No Double-Counting Credit Ledger:
                        </span>
                        {pkgMatch.credits.map((cr: any) => (
                          <div key={cr.id} className="mt-0.5">
                            &bull; {cr.credit_reason}
                          </div>
                        ))}
                      </div>
                    )}

                    <Button
                      onClick={() => setSelectedPackageId(pkgMatch.id)}
                      variant={isSelected ? "primary" : "outline"}
                      className="w-full text-xs"
                    >
                      {isSelected ? "Selected Package" : "Select This Package"}
                    </Button>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          <div className="flex justify-between items-center pt-4">
            <Button variant="outline" onClick={() => setActiveTab("tourism")}>
              &larr; Back to Tourism
            </Button>
            <Button onClick={() => setActiveTab("finalize")}>Next: Finalize & Review Plan &rarr;</Button>
          </div>
        </div>
      )}

      {/* TAB 4: FINALIZE PLAN */}
      {activeTab === "finalize" && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Finalize Your Medical Tourism Plan</CardTitle>
              <CardDescription>
                Review your customized hospital offering, included destinations, and total financial commitment.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Plan Title</label>
                <input
                  type="text"
                  value={planTitle}
                  onChange={(e) => setPlanTitle(e.target.value)}
                  className="w-full rounded-md border border-slate-300 p-2.5 text-sm focus:border-brand-blue focus:outline-none focus:ring-1 focus:ring-brand-blue"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-slate-50 rounded-lg border border-slate-200 text-sm">
                <div>
                  <span className="text-xs text-slate-500 block">Matched Healthcare Facility</span>
                  <span className="font-bold text-slate-900">{hospital?.name}</span>
                  <span className="block text-xs text-slate-600 mt-0.5">
                    {offering?.treatment_category?.name} ({hospital?.city?.name}, India)
                  </span>
                </div>

                <div>
                  <span className="text-xs text-slate-500 block">Selected Travel Package</span>
                  <span className="font-bold text-slate-900">
                    {selectedPkg?.travel_package?.name || "Direct Self-Guided Travel"}
                  </span>
                  {selectedPkg && (
                    <span className="block text-xs text-brand-green mt-0.5">
                      Effective Incremental Cost: {scenario.scenario_currency} {pkgEffectiveCost.toFixed(2)}
                    </span>
                  )}
                </div>
              </div>

              <div>
                <span className="text-sm font-semibold text-slate-700 block mb-2">
                  Curated Tourism Stops ({selectedDestinationIds.length} Selected)
                </span>
                <div className="space-y-2">
                  {destinations
                    .filter((d) => selectedDestinationIds.includes(d.destination.id))
                    .map((d, idx) => (
                      <div
                        key={d.id}
                        className="flex items-center justify-between p-3 bg-white border border-slate-200 rounded text-sm"
                      >
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-slate-400 text-xs">#{idx + 1}</span>
                          <span className="font-medium text-slate-800">{d.destination.name}</span>
                          <span className="text-xs text-slate-500">({d.destination.city?.name})</span>
                        </div>
                        <Badge variant="default">{d.tourism_scope.replace(/_/g, " ")}</Badge>
                      </div>
                    ))}
                </div>
              </div>

              {/* Total Estimated Commitment */}
              <div className="p-4 bg-blue-50/60 rounded-lg border border-blue-200 flex justify-between items-center">
                <div>
                  <span className="text-xs text-slate-600 uppercase tracking-wider block font-semibold">
                    Total Estimated Financial Commitment
                  </span>
                  <span className="text-xs text-slate-500">
                    Mandatory Hospital Ledger ({scenario.scenario_currency} {mandatoryTotal.toFixed(2)}) + Package Effective
                    Cost ({scenario.scenario_currency} {pkgEffectiveCost.toFixed(2)})
                  </span>
                </div>
                <div className="text-2xl font-bold text-brand-primary">
                  {scenario.scenario_currency} {(mandatoryTotal + pkgEffectiveCost).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </div>
              </div>

              <div className="space-y-4 pt-4">
                <MedicalSafetyDisclaimer />
                <FinancialSafetyDisclaimer />
              </div>

              <div className="flex justify-end pt-4">
                <Button
                  onClick={handleSaveFinalPlan}
                  disabled={savingPlan}
                  className="bg-brand-green text-white hover:bg-green-700"
                >
                  {savingPlan ? "Saving Plan..." : "Confirm & Save Final Plan"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
