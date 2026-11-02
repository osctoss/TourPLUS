"use client";

import React, { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Alert } from "@/components/ui/alert";
import { useAuth } from "@/app/providers";
import { apiClient } from "@/lib/api-client";

export default function ProfilePage() {
  const { user, profile, refreshUser } = useAuth();
  const [fullName, setFullName] = useState("");
  const [currency, setCurrency] = useState("USD");
  const [originCountryCode, setOriginCountryCode] = useState("GB");
  const [phone, setPhone] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (profile) {
      setFullName(profile.full_name || "");
      setCurrency(profile.display_currency || "USD");
      setOriginCountryCode(profile.origin_country_code || "GB");
    }
  }, [profile]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    setError(null);
    setIsLoading(true);

    try {
      await apiClient.patch("/auth/profile/", {
        full_name: fullName,
        display_currency: currency,
        origin_country_code: originCountryCode,
        phone_number: phone,
      });
      await refreshUser();
      setMessage("Profile preferences successfully updated.");
    } catch (err: any) {
      setError(err.message || "Failed to update profile.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="py-12 container mx-auto px-4 max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-primary">Patient Profile & Planning Preferences</h1>
        <p className="text-sm text-muted">Manage your default planning currency, origin location, and contact information.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Account Details</CardTitle>
          <CardDescription>Primary login: {user?.email || "Signed In"}</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {message && <Alert variant="success">{message}</Alert>}
            {error && <Alert variant="danger">{error}</Alert>}

            <Input
              label="Full Name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="block text-xs font-semibold uppercase tracking-wider text-muted">
                  Default Display Currency
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

              <div className="space-y-1.5">
                <label className="block text-xs font-semibold uppercase tracking-wider text-muted">
                  Country of Origin
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
                </select>
              </div>
            </div>

            <Input
              label="Contact Phone Number (Optional)"
              placeholder="+44 7911 123456"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
            />

            <Button type="submit" variant="green" isLoading={isLoading} className="mt-2">
              Save Preferences
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

