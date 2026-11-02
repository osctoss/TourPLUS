import React from "react";
import Link from "next/link";
import { 
  Building2, 
  Calculator, 
  Palmtree, 
  PackageCheck, 
  ArrowRight, 
  CheckCircle2, 
  ShieldCheck, 
  Sparkles,
  HeartPulse,
  Bone,
  Activity
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MedicalSafetyDisclaimer, FinancialSafetyDisclaimer } from "@/components/feedback/disclaimer";

export default function LandingPage() {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-blue-light/50 via-white to-surface py-16 sm:py-24 border-b border-border">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-5xl text-center space-y-6">
          <Badge variant="success" className="mb-2 py-1 px-3 text-xs uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5 mr-1 text-green" />
            Decision-Support Engine for Medical Travel
          </Badge>
          
          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold text-primary tracking-tight leading-[1.15]">
            Plan your medical journey to India with <span className="text-blue">greater clarity</span> and <span className="text-green">confidence</span>.
          </h1>
          
          <p className="text-base sm:text-xl text-muted max-w-3xl mx-auto leading-relaxed">
            Connect verified hospital offerings, itemized financial scenarios, recovery-aware tourism, and travel agency package matching into one transparent plan.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link href="/plan/new">
              <Button variant="green" size="lg" className="w-full sm:w-auto shadow-md">
                Start Planning Your Journey
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </Link>
            <Link href="/how-it-works">
              <Button variant="outline" size="lg" className="w-full sm:w-auto">
                Explore How It Works
              </Button>
            </Link>
          </div>

          {/* Core Specialties Pills */}
          <div className="pt-8 flex flex-wrap items-center justify-center gap-3">
            <span className="text-xs font-semibold text-muted uppercase tracking-wider mr-2">Target Specialties:</span>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-white border border-border rounded-full text-xs font-medium text-primary shadow-subtle">
              <HeartPulse className="w-3.5 h-3.5 text-danger" /> Cardiology
            </div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-white border border-border rounded-full text-xs font-medium text-primary shadow-subtle">
              <Bone className="w-3.5 h-3.5 text-blue" /> Orthopedics
            </div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-white border border-border rounded-full text-xs font-medium text-primary shadow-subtle">
              <Activity className="w-3.5 h-3.5 text-green" /> Oncology
            </div>
          </div>
        </div>
      </section>

      {/* 4 Pillars Section */}
      <section className="py-16 sm:py-20 bg-white">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl">
          <div className="text-center max-w-2xl mx-auto mb-12 space-y-3">
            <h2 className="text-2xl sm:text-3xl font-bold text-primary">The 4-Pillar Decision Framework</h2>
            <p className="text-sm sm:text-base text-muted">
              We evaluate every prospective hospital with its own independent financial and geographic context.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="hover:border-blue/50 transition-all">
              <CardHeader>
                <div className="w-10 h-10 rounded-lg bg-blue-light flex items-center justify-center text-blue mb-2">
                  <Building2 className="w-5 h-5" />
                </div>
                <CardTitle className="text-base">1. Hospital Discovery</CardTitle>
                <CardDescription>
                  Verified specialty offerings filtered by clinical scope, accreditation, and international patient amenities.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="hover:border-green/50 transition-all">
              <CardHeader>
                <div className="w-10 h-10 rounded-lg bg-green-mint flex items-center justify-center text-green mb-2">
                  <Calculator className="w-5 h-5" />
                </div>
                <CardTitle className="text-base">2. Scenario Budgeting</CardTitle>
                <CardDescription>
                  Independent financial ledgers covering treatment, flights, hotel stays, visas, and discretionary tourism funds.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="hover:border-cyan/50 transition-all">
              <CardHeader>
                <div className="w-10 h-10 rounded-lg bg-cyan-light flex items-center justify-center text-cyan mb-2">
                  <Palmtree className="w-5 h-5" />
                </div>
                <CardTitle className="text-base">3. Recovery Tourism</CardTitle>
                <CardDescription>
                  3-tier scope recommendations (Local, State, National) respecting post-treatment recovery and travel limits.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="hover:border-primary/50 transition-all">
              <CardHeader>
                <div className="w-10 h-10 rounded-lg bg-surface flex items-center justify-center text-primary mb-2">
                  <PackageCheck className="w-5 h-5" />
                </div>
                <CardTitle className="text-base">4. Dynamic Package Credit</CardTitle>
                <CardDescription>
                  Package matching with inclusion credits that eliminate double-charging for hotel nights and transfers.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* Disclaimers & Safety */}
      <section className="py-12 bg-surface border-t border-border">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl space-y-4">
          <MedicalSafetyDisclaimer />
          <FinancialSafetyDisclaimer />
        </div>
      </section>
    </div>
  );
}

