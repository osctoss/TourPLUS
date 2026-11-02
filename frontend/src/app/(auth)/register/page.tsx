"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Alert } from "@/components/ui/alert";
import { useAuth } from "@/app/providers";
import { apiClient } from "@/lib/api-client";

export default function RegisterPage() {
  const router = useRouter();
  const { login, refreshUser } = useAuth();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [originCountryCode, setOriginCountryCode] = useState("GB");
  const [currency, setCurrency] = useState("USD");
  const [consentAccepted, setConsentAccepted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!consentAccepted) {
      setError("Please accept the terms and consent to data processing for medical planning.");
      return;
    }
    setError(null);
    setIsLoading(true);

    try {
      const data: any = await apiClient.post("/auth/register/", {
        email,
        password,
        full_name: fullName,
        origin_country_code: originCountryCode,
        display_currency: currency,
        consent_accepted: true,
      });
      login(data.user);
      await refreshUser();
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Registration failed. Please check the inputs.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="py-12 sm:py-20 container mx-auto px-4 max-w-lg">
      <Card>
        <CardHeader className="text-center space-y-2">
          <CardTitle className="text-2xl font-bold">Create Patient Account</CardTitle>
          <CardDescription>
            Begin planning your personalized medical travel journey to India.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert variant="danger">
                {error}
              </Alert>
            )}

            <Input
              label="Full Name"
              type="text"
              placeholder="e.g. Sarah Jenkins"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />

            <Input
              label="Email Address"
              type="email"
              placeholder="patient@example.com"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />

            <Input
              label="Password (min 8 characters)"
              type="password"
              placeholder="••••••••"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="block text-xs font-semibold uppercase tracking-wider text-muted">
                  Origin Country
                </label>
                <select
                  className="flex h-10 w-full rounded-lg border border-border bg-white px-3 py-2 text-sm text-body focus:border-blue focus:outline-none"
                  value={originCountryCode}
                  onChange={(e) => setOriginCountryCode(e.target.value)}
                >
                  <option value="GB">United Kingdom (GB)</option>
                  <option value="US">United States (US)</option>
                  <option value="CA">Canada (CA)</option>
                  <option value="AU">Australia (AU)</option>
                  <option value="AE">UAE (AE)</option>
                  <option value="OTHER">Other</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="block text-xs font-semibold uppercase tracking-wider text-muted">
                  Display Currency
                </label>
                <select
                  className="flex h-10 w-full rounded-lg border border-border bg-white px-3 py-2 text-sm text-body focus:border-blue focus:outline-none"
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                >
                  <option value="USD">USD ($)</option>
                  <option value="GBP">GBP (£)</option>
                  <option value="EUR">EUR (€)</option>
                  <option value="AED">AED (AED)</option>
                  <option value="INR">INR (₹)</option>
                </select>
              </div>
            </div>

            <div className="pt-2 flex items-start gap-2.5">
              <input
                id="consent"
                type="checkbox"
                required
                checked={consentAccepted}
                onChange={(e) => setConsentAccepted(e.target.checked)}
                className="mt-1 h-4 w-4 rounded border-border text-green focus:ring-green"
              />
              <label htmlFor="consent" className="text-xs text-muted leading-relaxed">
                I consent to the processing of my travel and medical preference data for informational decision support. I acknowledge TourPlus AI does not diagnose conditions or guarantee medical outcomes.
              </label>
            </div>

            <Button type="submit" variant="green" size="md" className="w-full mt-4" isLoading={isLoading}>
              Complete Registration
            </Button>
          </form>
        </CardContent>
        <CardFooter className="justify-center text-xs text-muted">
          Already registered?{" "}
          <Link href="/login" className="text-blue font-semibold ml-1 hover:underline">
            Sign In here
          </Link>
        </CardFooter>
      </Card>
    </div>
  );
}
