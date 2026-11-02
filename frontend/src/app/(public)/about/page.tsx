import React from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { ShieldCheck, HeartPulse, Scale, CheckCircle2 } from "lucide-react";
import { MedicalSafetyDisclaimer, FinancialSafetyDisclaimer } from "@/components/feedback/disclaimer";

export default function AboutPage() {
  return (
    <div className="py-12 sm:py-16">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl space-y-12">
        <div className="text-center space-y-4">
          <Badge variant="info">Mission & Principles</Badge>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-primary">
            About TourPlus AI
          </h1>
          <p className="text-muted max-w-2xl mx-auto text-sm sm:text-base">
            Dedicated to bringing clinical safety, financial integrity, and geographic transparency to international medical travelers visiting India.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <HeartPulse className="w-8 h-8 text-danger mb-2" />
              <CardTitle className="text-base">Medical Safety First</CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted leading-relaxed">
              We never diagnose conditions or prescribe treatments. Recommendations strictly observe clinician travel advice and recovery restrictions.
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Scale className="w-8 h-8 text-green mb-2" />
              <CardTitle className="text-base">Zero Double-Counting</CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted leading-relaxed">
              Our Dynamic Inclusion Credit ledger ensures services included in travel packages (like airport cabs or hotels) are credited against your mandatory expenses.
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <ShieldCheck className="w-8 h-8 text-blue mb-2" />
              <CardTitle className="text-base">Verifiable Provenance</CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted leading-relaxed">
              We visibly distinguish verified provider data from indicative estimates. We never present demonstration records as real-world facts.
            </CardContent>
          </Card>
        </div>

        <div className="space-y-4 pt-6">
          <MedicalSafetyDisclaimer />
          <FinancialSafetyDisclaimer />
        </div>
      </div>
    </div>
  );
}

