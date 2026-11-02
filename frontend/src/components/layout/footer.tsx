import React from "react";
import Link from "next/link";

export function Footer() {
  return (
    <footer className="w-full border-t border-border bg-white mt-auto">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="h-7 w-7 rounded bg-primary flex items-center justify-center text-white font-heading font-bold text-sm">
                T+
              </div>
              <span className="font-heading font-bold text-primary">TourPlus AI</span>
            </div>
            <p className="text-xs text-muted leading-relaxed">
              AI-assisted, patient-centric decision-support platform for personalized medical tourism in India.
            </p>
          </div>

          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-primary mb-3">Core Specialties</h4>
            <ul className="space-y-2 text-xs text-muted">
              <li>Cardiology & Heart Surgery</li>
              <li>Orthopedics & Joint Replacement</li>
              <li>Oncology & Precision Therapy</li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-primary mb-3">Platform</h4>
            <ul className="space-y-2 text-xs text-muted">
              <li><Link href="/how-it-works" className="hover:text-primary">How It Works</Link></li>
              <li><Link href="/about" className="hover:text-primary">About TourPlus AI</Link></li>
              <li><Link href="/plan/new" className="hover:text-primary">Patient Assessment</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-primary mb-3">Data & Governance</h4>
            <ul className="space-y-2 text-xs text-muted">
              <li>Verified Provider Catalogue</li>
              <li>Clinical Safety Disclaimers</li>
              <li>Dynamic Package Credit Logic</li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-border flex flex-col sm:flex-row items-center justify-between text-xs text-muted gap-4">
          <p>&copy; {new Date().getFullYear()} TourPlus AI. All rights reserved.</p>
          <div className="flex items-center gap-4">
            <span className="text-muted/60">Decision Support System — India</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

