import React from "react";
import Link from "next/link";
import { ArrowRight, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MedicalSafetyDisclaimer, FinancialSafetyDisclaimer } from "@/components/feedback/disclaimer";

export default function HowItWorksPage() {
  const steps = [
    {
      step: "01",
      title: "Structured Intake & Medical Requirement",
      desc: "Tell us your required medical specialty (Cardiology, Orthopedics, Oncology), origin country, travel group size, and total planning budget.",
    },
    {
      step: "02",
      title: "Hospital Filtering & Independent Scenarios",
      desc: "Our engine discovers matching hospitals with verified treatment offerings and generates a discrete scenario for every eligible hospital.",
    },
    {
      step: "03",
      title: "Mandatory Ledger & Discretionary Budget",
      desc: "Mandatory costs (treatment, international flights, lodging, visas, local transit) are calculated. If the budget allows, discretionary tourism funds are identified.",
    },
    {
      step: "04",
      title: "Recovery-Aware 3-Tier Tourism",
      desc: "We recommend feasible destinations across Local/Regional, State-Level, and National scopes based on your recovery constraints and travel window.",
    },
    {
      step: "05",
      title: "Dynamic Package Inclusion Credit",
      desc: "Curated travel packages covering recommended destinations are evaluated. If a package includes hotel nights or transfers, credit is applied to eliminate double-counting.",
    },
    {
      step: "06",
      title: "Final Transparent Itinerary",
      desc: "Review your side-by-side hospital options, select your preferred package, and export your itemized medical tourism plan.",
    },
  ];

  return (
    <div className="py-12 sm:py-16">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl space-y-10">
        <div className="text-center space-y-4">
          <Badge variant="info">End-to-End Decision Journey</Badge>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-primary">
            How TourPlus AI Works
          </h1>
          <p className="text-muted max-w-2xl mx-auto text-sm sm:text-base">
            A step-by-step decision framework connecting healthcare discovery, financial feasibility, recovery safety, and curated travel.
          </p>
        </div>

        <div className="space-y-6">
          {steps.map((item) => (
            <Card key={item.step} className="flex flex-col sm:flex-row gap-6 p-6 items-start">
              <div className="w-12 h-12 rounded-xl bg-primary text-white flex items-center justify-center font-heading font-bold text-lg shrink-0">
                {item.step}
              </div>
              <div className="space-y-2">
                <CardTitle className="text-lg">{item.title}</CardTitle>
                <p className="text-sm text-muted leading-relaxed">{item.desc}</p>
              </div>
            </Card>
          ))}
        </div>

        <div className="p-8 rounded-card bg-green-mint border border-green/20 text-center space-y-4">
          <h3 className="text-xl font-bold text-primary">Ready to explore your options?</h3>
          <p className="text-sm text-muted max-w-md mx-auto">
            Start a planning assessment now. No booking fees, no unverified claims.
          </p>
          <Link href="/plan/new">
            <Button variant="green" size="lg">
              Begin Free Assessment
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </Link>
        </div>

        <div className="space-y-4 pt-4">
          <MedicalSafetyDisclaimer />
          <FinancialSafetyDisclaimer />
        </div>
      </div>
    </div>
  );
}

