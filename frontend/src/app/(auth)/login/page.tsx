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

export default function LoginPage() {
  const router = useRouter();
  const { login, refreshUser } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const data: any = await apiClient.post("/auth/login/", { email, password });
      login(data.user);
      await refreshUser();
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Failed to sign in. Please verify your credentials.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="py-16 sm:py-24 container mx-auto px-4 max-w-md">
      <Card>
        <CardHeader className="text-center space-y-2">
          <CardTitle className="text-2xl font-bold">Sign In to TourPlus AI</CardTitle>
          <CardDescription>
            Access your saved medical scenarios, budget ledgers, and personalized itineraries.
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
              label="Email Address"
              type="email"
              placeholder="patient@example.com"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />

            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />

            <Button type="submit" variant="green" size="md" className="w-full mt-2" isLoading={isLoading}>
              Sign In
            </Button>
          </form>
        </CardContent>
        <CardFooter className="justify-center text-xs text-muted">
          Don&apos;t have an account?{" "}
          <Link href="/register" className="text-blue font-semibold ml-1 hover:underline">
            Register here
          </Link>
        </CardFooter>
      </Card>
    </div>
  );
}

