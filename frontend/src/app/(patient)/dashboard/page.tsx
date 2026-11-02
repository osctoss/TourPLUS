"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { PlusCircle, FileText, Compass, Calendar, ArrowRight, Building2, ShieldAlert } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/app/providers";
import { apiClient } from "@/lib/api-client";
import { MedicalSafetyDisclaimer } from "@/components/feedback/disclaimer";

export default function DashboardPage() {
  const { user, profile } = useAuth();
  const [requests, setRequests] = useState<any[]>([]);
  const [finalPlans, setFinalPlans] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [reqData, planData]: [any, any] = await Promise.all([
          apiClient.get("/trip-requests/").catch(() => []),
          apiClient.get("/final-plans/").catch(() => []),
        ]);
        setRequests(Array.isArray(reqData) ? reqData : reqData.results || []);
        setFinalPlans(Array.isArray(planData) ? planData : planData.results || []);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="py-10 container mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-surface p-6 rounded-card border border-border">
        <div>
          <h1 className="text-2xl font-bold text-primary">
            Welcome back, {profile?.full_name || user?.email || "Patient"}
          </h1>
          <p className="text-sm text-muted mt-1">
            Manage your medical tourism requests, compare hospital scenarios, and access saved itineraries.
          </p>
        </div>
        <Link href="/plan/new">
          <Button variant="green" size="md" className="shrink-0">
            <PlusCircle className="w-4 h-4 mr-2" />
            Start New Medical Request
          </Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Active Planning Requests */}
        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div>
                <CardTitle className="text-lg">Your Medical Travel Requests</CardTitle>
                <CardDescription>Submitted and in-progress scenario runs</CardDescription>
              </div>
              <Link href="/plan/new">
                <Button variant="outline" size="sm">
                  + New Request
                </Button>
              </Link>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="py-8 text-center text-sm text-muted">Loading your requests...</div>
              ) : requests.length === 0 ? (
                <div className="py-10 text-center space-y-3">
                  <div className="w-12 h-12 rounded-full bg-blue-light text-blue mx-auto flex items-center justify-center">
                    <FileText className="w-6 h-6" />
                  </div>
                  <h4 className="text-sm font-semibold text-primary">No medical requests yet</h4>
                  <p className="text-xs text-muted max-w-sm mx-auto">
                    Submit your known medical condition and budget to receive transparent hospital scenarios and tourism plans.
                  </p>
                  <Link href="/plan/new">
                    <Button variant="green" size="sm" className="mt-2">
                      Start Your Assessment
                    </Button>
                  </Link>
                </div>
              ) : (
                <div className="divide-y divide-border/60">
                  {requests.map((req) => (
                    <div key={req.id} className="py-4 flex items-center justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-sm text-primary">
                            {req.specialty_name || "Specialty Evaluation"}
                          </span>
                          <Badge variant={req.status === "COMPLETED" ? "success" : "info"}>
                            {req.status}
                          </Badge>
                        </div>
                        <p className="text-xs text-muted mt-1">
                          Budget: {req.budget_currency} {req.total_budget_amount} • {req.party_size} Traveller(s) • {req.available_days} Days
                        </p>
                      </div>
                      <Link href={`/plan/${req.id}/results`}>
                        <Button variant="ghost" size="sm">
                          View Scenarios
                          <ArrowRight className="w-4 h-4 ml-1.5" />
                        </Button>
                      </Link>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Saved Final Plans */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Saved Final Plans</CardTitle>
              <CardDescription>Finalized itineraries ready for consultation and export</CardDescription>
            </CardHeader>
            <CardContent>
              {finalPlans.length === 0 ? (
                <div className="py-8 text-center text-xs text-muted">
                  No finalized plans yet. Compare scenarios and select your preferred hospital to build a final plan.
                </div>
              ) : (
                <div className="divide-y divide-border/60">
                  {finalPlans.map((plan) => (
                    <div key={plan.id} className="py-3 flex items-center justify-between">
                      <div>
                        <span className="font-medium text-sm text-primary">{plan.plan_title}</span>
                        <p className="text-xs text-muted">{plan.selected_scope} Scope</p>
                      </div>
                      <Link href={`/final-plan/${plan.id}`}>
                        <Button variant="outline" size="sm">
                          View Plan
                        </Button>
                      </Link>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar Info */}
        <div className="space-y-6">
          <Card className="bg-surface border-border">
            <CardHeader>
              <CardTitle className="text-sm font-bold uppercase tracking-wider text-muted">
                Decision Support Guide
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-xs text-muted leading-relaxed">
              <p>
                <strong className="text-primary block mb-0.5">Independent Scenarios:</strong>
                Each hospital candidate has its own budget ledger, travel distance, and local package options.
              </p>
              <p>
                <strong className="text-primary block mb-0.5">Dynamic Credit:</strong>
                When an agency package covers hotel nights or cabs, that amount is credited back into your spendable tourism budget.
              </p>
              <p>
                <strong className="text-primary block mb-0.5">Recovery Boundary:</strong>
                Tourism suggestions adapt to your recovery duration. Confirm all activities with your treating doctor.
              </p>
            </CardContent>
          </Card>

          <MedicalSafetyDisclaimer />
        </div>
      </div>
    </div>
  );
}

