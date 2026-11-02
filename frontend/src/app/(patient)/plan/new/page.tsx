"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api-client";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Alert } from "@/components/ui/alert";
import { MedicalSafetyDisclaimer, FinancialSafetyDisclaimer } from "@/components/feedback/disclaimer";

interface Category {
  id: string;
  name: string;
  slug: string;
  specialty?: string;
  description?: string;
}

interface Specialty {
  id: string;
  name: string;
  slug: string;
  description: string;
}

interface DestinationCategory {
  id: string;
  name: string;
  slug: string;
}

interface Country {
  id: string;
  name: string;
  iso2: string;
  default_currency: string;
}

export default function NewPlanAssessmentPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Catalogue data
  const [specialties, setSpecialties] = useState<Specialty[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [destCategories, setDestCategories] = useState<DestinationCategory[]>([]);
  const [countries, setCountries] = useState<Country[]>([]);

  // Assessment form state
  const [originCountry, setOriginCountry] = useState("");
  const [budgetCurrency, setBudgetCurrency] = useState("USD");
  const [partySize, setPartySize] = useState(1);
  const [availableDays, setAvailableDays] = useState(14);
  const [preferredArrivalDate, setPreferredArrivalDate] = useState("");

  const [selectedSpecialty, setSelectedSpecialty] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [knownConditionText, setKnownConditionText] = useState("");

  const [recoveryDays, setRecoveryDays] = useState(7);
  const [clinicianGuidance, setClinicianGuidance] = useState("NOT_PROVIDED");
  const [travelIntensity, setTravelIntensity] = useState("LOW");

  const [totalBudget, setTotalBudget] = useState("15000");

  const [selectedInterests, setSelectedInterests] = useState<Record<string, number>>({});
  const [disclaimerConfirmed, setDisclaimerConfirmed] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        const [specRes, catRes, destCatRes, geoRes] = await Promise.all([
          apiClient.get<any>("/catalog/specialties/"),
          apiClient.get<any>("/catalog/treatment-categories/"),
          apiClient.get<any>("/tourism/categories/"),
          apiClient.get<any>("/geo/countries/"),
        ]);

        const specList = specRes.results || specRes || [];
        const catList = catRes.results || catRes || [];
        const destCatList = destCatRes.results || destCatRes || [];
        const countryList = geoRes.results || geoRes || [];

        setSpecialties(specList);
        setCategories(catList);
        setDestCategories(destCatList);
        setCountries(countryList);

        if (specList.length > 0) setSelectedSpecialty(specList[0].id);
        if (countryList.length > 0) setOriginCountry(countryList[0].id);
      } catch (err: any) {
        setError("Failed to load clinical and tourism catalogue options. Please check your connection.");
      }
    }
    loadData();
  }, []);

  const filteredCategories = categories.filter(
    (c) => !selectedSpecialty || c.specialty === selectedSpecialty || (c as any).specialty_id === selectedSpecialty
  );

  const toggleInterest = (catId: string) => {
    setSelectedInterests((prev) => {
      const copy = { ...prev };
      if (copy[catId]) {
        delete copy[catId];
      } else {
        copy[catId] = 3;
      }
      return copy;
    });
  };

  const setInterestWeight = (catId: string, weight: number) => {
    setSelectedInterests((prev) => ({
      ...prev,
      [catId]: weight,
    }));
  };

  const handleNext = () => {
    setError(null);
    if (currentStep === 1) {
      if (partySize < 1 || availableDays < 3) {
        setError("Party size must be at least 1 and trip duration at least 3 days.");
        return;
      }
    } else if (currentStep === 2) {
      if (!selectedSpecialty) {
        setError("Please select a medical specialty.");
        return;
      }
    } else if (currentStep === 4) {
      if (!totalBudget || parseFloat(totalBudget) <= 0) {
        setError("Please enter a valid total budget amount.");
        return;
      }
    }
    setCurrentStep((prev) => Math.min(6, prev + 1));
  };

  const handlePrev = () => {
    setError(null);
    setCurrentStep((prev) => Math.max(1, prev - 1));
  };

  const handleSubmitAndGenerate = async () => {
    if (!disclaimerConfirmed) {
      setError("You must acknowledge the Medical Safety and Planning Disclaimers before generating a plan.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // 1. Create Trip Request with nested interests
      const interestsInput = Object.entries(selectedInterests).map(([catId, weight]) => ({
        destination_category: catId,
        preference_weight: weight,
      }));

      const tripPayload = {
        origin_country: originCountry || undefined,
        specialty: selectedSpecialty || undefined,
        treatment_category: selectedCategory || undefined,
        known_condition_text: knownConditionText,
        total_budget_amount: totalBudget,
        budget_currency: budgetCurrency,
        party_size: partySize,
        available_days: availableDays,
        recovery_duration_days: recoveryDays,
        preferred_arrival_date: preferredArrivalDate || undefined,
        clinician_travel_guidance_status: clinicianGuidance,
        travel_intensity_preference: travelIntensity,
        interests_input: interestsInput,
      };

      const tripRequest = await apiClient.post<any>("/trip-requests/", tripPayload);

      // 2. Generate Plan Orchestration
      await apiClient.post<any>(`/trip-requests/${tripRequest.id}/generate-plan/`);

      // 3. Route to Scenario Comparison Results
      router.push(`/plan/${tripRequest.id}/results`);
    } catch (err: any) {
      setError(err.message || "Failed to generate recommendation plan. Please try again.");
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Wizard Progress Bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
          <span>Step {currentStep} of 6</span>
          <span>
            {currentStep === 1 && "Origin & Travel Party"}
            {currentStep === 2 && "Medical Requirement"}
            {currentStep === 3 && "Recovery & Constraints"}
            {currentStep === 4 && "Financial Parameters"}
            {currentStep === 5 && "Tourism Preferences"}
            {currentStep === 6 && "Review & Consent"}
          </span>
        </div>
        <div className="w-full bg-slate-200 h-2.5 rounded-full overflow-hidden">
          <div
            className="bg-brand-blue h-full transition-all duration-300"
            style={{ width: `${(currentStep / 6) * 100}%` }}
          />
        </div>
      </div>

      {error && (
        <Alert variant="danger" title="Assessment Notice" className="mb-6">
          {error}
        </Alert>
      )}

      {/* Step 1: Origin & Travel Details */}
      {currentStep === 1 && (
        <Card>
          <CardHeader>
            <CardTitle>Travel Party & Schedule</CardTitle>
            <CardDescription>
              Help us tailor travel logistics, return flight multipliers, and recovery lodging schedules.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Country of Origin
              </label>
              <select
                value={originCountry}
                onChange={(e) => setOriginCountry(e.target.value)}
                className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-brand-blue focus:outline-none focus:ring-1 focus:ring-brand-blue"
              >
                {countries.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} ({c.default_currency})
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Travel Party Size (Patients + Companions)
                </label>
                <Input
                  type="number"
                  min={1}
                  max={10}
                  value={partySize}
                  onChange={(e) => setPartySize(parseInt(e.target.value) || 1)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Trip Duration (Total Available Days)
                </label>
                <Input
                  type="number"
                  min={3}
                  max={60}
                  value={availableDays}
                  onChange={(e) => setAvailableDays(parseInt(e.target.value) || 14)}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Preferred Arrival Date (Optional)
              </label>
              <Input
                type="date"
                value={preferredArrivalDate}
                onChange={(e) => setPreferredArrivalDate(e.target.value)}
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 2: Medical Requirement */}
      {currentStep === 2 && (
        <Card>
          <CardHeader>
            <CardTitle>Medical Offering & Specialty</CardTitle>
            <CardDescription>
              Select the verified specialty and procedure category required.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Medical Specialty
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {specialties.map((spec) => (
                  <button
                    type="button"
                    key={spec.id}
                    onClick={() => {
                      setSelectedSpecialty(spec.id);
                      setSelectedCategory("");
                    }}
                    className={`p-4 text-left rounded-lg border text-sm font-medium transition-colors ${
                      selectedSpecialty === spec.id
                        ? "border-brand-blue bg-blue-50 text-brand-primary font-semibold ring-2 ring-brand-blue"
                        : "border-slate-200 hover:border-slate-300 text-slate-700 bg-white"
                    }`}
                  >
                    <div className="text-base font-bold mb-1">{spec.name}</div>
                    <div className="text-xs text-slate-500 line-clamp-2">{spec.description}</div>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Treatment Procedure Category
              </label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-brand-blue focus:outline-none focus:ring-1 focus:ring-brand-blue"
              >
                <option value="">-- All Verified Procedures in Specialty --</option>
                {filteredCategories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Patient Notes & Condition Summary
              </label>
              <textarea
                rows={3}
                value={knownConditionText}
                onChange={(e) => setKnownConditionText(e.target.value)}
                placeholder="Include relevant clinical history, pre-existing conditions, mobility notes, or specific hospital requests..."
                className="w-full rounded-md border border-slate-300 p-3 text-sm focus:border-brand-blue focus:outline-none focus:ring-1 focus:ring-brand-blue"
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 3: Recovery & Travel Constraints */}
      {currentStep === 3 && (
        <Card>
          <CardHeader>
            <CardTitle>Recovery & Travel Safety Boundaries</CardTitle>
            <CardDescription>
              We protect clinical recovery by enforcing safe transit and clinician clearance boundaries.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Expected Post-Procedure Recovery Days
                </label>
                <Input
                  type="number"
                  min={1}
                  max={30}
                  value={recoveryDays}
                  onChange={(e) => setRecoveryDays(parseInt(e.target.value) || 7)}
                />
                <p className="text-xs text-slate-500 mt-1">
                  Days allocated for dedicated clinical observation and in-room rest before leisure transit.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Clinician Travel Clearance Status
                </label>
                <select
                  value={clinicianGuidance}
                  onChange={(e) => setClinicianGuidance(e.target.value)}
                  className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-brand-blue focus:outline-none focus:ring-1 focus:ring-brand-blue"
                >
                  <option value="NOT_PROVIDED">Requires Clinician Confirmation</option>
                  <option value="PROVIDED">Confirmed Guidance Provided</option>
                </select>
                <p className="text-xs text-slate-500 mt-1">
                  {clinicianGuidance === "NOT_PROVIDED"
                    ? "Destinations will be flagged for review until confirmed with your treating doctor."
                    : "Guidance reviewed with your doctor."}
                </p>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Post-Recovery Travel Intensity Preference
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {[
                  { id: "LOW", title: "Low / Gentle", desc: "Short rides, level walkways, scenic relaxation" },
                  { id: "MODERATE", title: "Moderate", desc: "Museum visits, light walking, regional day trips" },
                  { id: "HIGH", title: "Active Sightseeing", desc: "Full-day excursions, extended transit" },
                ].map((tier) => (
                  <button
                    type="button"
                    key={tier.id}
                    onClick={() => setTravelIntensity(tier.id)}
                    className={`p-3 text-left rounded-lg border text-sm transition-colors ${
                      travelIntensity === tier.id
                        ? "border-brand-green bg-green-50 text-slate-900 font-semibold ring-2 ring-brand-green"
                        : "border-slate-200 text-slate-700 bg-white"
                    }`}
                  >
                    <div className="font-bold">{tier.title}</div>
                    <div className="text-xs text-slate-500">{tier.desc}</div>
                  </button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 4: Financial Parameters */}
      {currentStep === 4 && (
        <Card>
          <CardHeader>
            <CardTitle>Budget & Financial Parameters</CardTitle>
            <CardDescription>
              Our ledger calculates mandatory hospital expenses first, reserving remaining funds for tourism.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Total Travel & Medical Budget
                </label>
                <Input
                  type="number"
                  min={1000}
                  step={500}
                  value={totalBudget}
                  onChange={(e) => setTotalBudget(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Currency
                </label>
                <select
                  value={budgetCurrency}
                  onChange={(e) => setBudgetCurrency(e.target.value)}
                  className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-brand-blue focus:outline-none focus:ring-1 focus:ring-brand-blue"
                >
                  <option value="USD">USD ($)</option>
                  <option value="EUR">EUR (€)</option>
                  <option value="GBP">GBP (£)</option>
                  <option value="AED">AED (د.إ)</option>
                  <option value="INR">INR (₹)</option>
                </select>
              </div>
            </div>

            <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 text-sm text-slate-600">
              <div className="font-semibold text-slate-900 mb-1">Transparent Financial Principle:</div>
              <p>
                TourPlus AI generates a deterministic Decimal budget ledger. The system reserves funds for medical treatment,
                return airfare, accredited hotel stay, visas, and local transit. Any excess forms your discretionary budget,
                and travel package credits are applied dynamically without double-counting.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 5: Tourism Preferences */}
      {currentStep === 5 && (
        <Card>
          <CardHeader>
            <CardTitle>Tourism & Leisure Interests</CardTitle>
            <CardDescription>
              Select your travel interests and prioritize them (1 = mild, 5 = high interest).
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {destCategories.map((cat) => {
                const isSelected = !!selectedInterests[cat.id];
                const weight = selectedInterests[cat.id] || 3;

                return (
                  <div
                    key={cat.id}
                    className={`p-4 rounded-lg border transition-all ${
                      isSelected ? "border-brand-blue bg-blue-50/50" : "border-slate-200 bg-white"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-slate-800 text-sm">{cat.name}</span>
                      <button
                        type="button"
                        onClick={() => toggleInterest(cat.id)}
                        className={`text-xs px-2.5 py-1 rounded-full font-semibold transition-colors ${
                          isSelected
                            ? "bg-brand-blue text-white"
                            : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                        }`}
                      >
                        {isSelected ? "Selected" : "Add"}
                      </button>
                    </div>

                    {isSelected && (
                      <div className="mt-3 pt-3 border-t border-slate-200/80">
                        <div className="flex justify-between text-xs text-slate-500 mb-1">
                          <span>Priority Weight:</span>
                          <span className="font-bold text-brand-blue">{weight} / 5</span>
                        </div>
                        <input
                          type="range"
                          min={1}
                          max={5}
                          value={weight}
                          onChange={(e) => setInterestWeight(cat.id, parseInt(e.target.value))}
                          className="w-full accent-brand-blue cursor-pointer"
                        />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 6: Review & Consent */}
      {currentStep === 6 && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Review Your Assessment Profile</CardTitle>
              <CardDescription>
                Confirm your input parameters before generating hospital scenarios and budgets.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-slate-500 block text-xs">Specialty</span>
                  <span className="font-semibold text-slate-800">
                    {specialties.find((s) => s.id === selectedSpecialty)?.name || "Not Specified"}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block text-xs">Procedure</span>
                  <span className="font-semibold text-slate-800">
                    {categories.find((c) => c.id === selectedCategory)?.name || "All in Specialty"}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block text-xs">Party Size</span>
                  <span className="font-semibold text-slate-800">{partySize} Traveler(s)</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-xs">Trip Duration</span>
                  <span className="font-semibold text-slate-800">{availableDays} Days</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-xs">Recovery Duration</span>
                  <span className="font-semibold text-slate-800">{recoveryDays} Days</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-xs">Total Budget</span>
                  <span className="font-semibold text-brand-green">
                    {budgetCurrency} {parseFloat(totalBudget).toLocaleString()}
                  </span>
                </div>
              </div>

              {knownConditionText && (
                <div className="mt-4 pt-4 border-t border-slate-200">
                  <span className="text-slate-500 block text-xs mb-1">Clinical Notes</span>
                  <p className="text-xs bg-slate-50 p-3 rounded border border-slate-200 text-slate-700">
                    {knownConditionText}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Mandatory Disclaimers */}
          <div className="space-y-4">
            <MedicalSafetyDisclaimer />
            <FinancialSafetyDisclaimer />
          </div>

          <div className="p-4 bg-white rounded-lg border border-slate-200 flex items-start space-x-3">
            <input
              type="checkbox"
              id="consent-check"
              checked={disclaimerConfirmed}
              onChange={(e) => setDisclaimerConfirmed(e.target.checked)}
              className="mt-1 h-4 w-4 rounded border-slate-300 text-brand-blue focus:ring-brand-blue"
            />
            <label htmlFor="consent-check" className="text-xs text-slate-700 leading-relaxed cursor-pointer">
              I understand and agree that TourPlus AI provides decision-support and planning information only. It is not a
              medical provider, and all treatments, medical visas, flights, and accommodations require direct medical
              evaluation and booking confirmation with accredited institutions.
            </label>
          </div>
        </div>
      )}

      {/* Navigation Buttons */}
      <div className="mt-8 flex justify-between items-center">
        {currentStep > 1 ? (
          <Button variant="outline" onClick={handlePrev} disabled={loading}>
            Back
          </Button>
        ) : (
          <div />
        )}

        {currentStep < 6 ? (
          <Button onClick={handleNext}>Next Step</Button>
        ) : (
          <Button
            onClick={handleSubmitAndGenerate}
            disabled={!disclaimerConfirmed || loading}
            className="bg-brand-blue text-white hover:bg-brand-primary"
          >
            {loading ? "Generating Recommendation Scenarios..." : "Generate Decision-Support Plan"}
          </Button>
        )}
      </div>
    </div>
  );
}

