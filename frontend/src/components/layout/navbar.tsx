import React from "react";
import Link from "next/link";
import { Compass, User, PlusCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-white/95 backdrop-blur">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="h-9 w-9 rounded-lg bg-primary flex items-center justify-center text-white font-heading font-bold text-lg shadow-sm">
            T+
          </div>
          <div className="flex flex-col">
            <span className="font-heading font-bold text-lg text-primary tracking-tight leading-none">
              TourPlus <span className="text-green">AI</span>
            </span>
            <span className="text-[10px] text-muted tracking-wider uppercase">Medical Tourism India</span>
          </div>
        </Link>

        <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-muted">
          <Link href="/" className="hover:text-primary transition-colors">
            Home
          </Link>
          <Link href="/how-it-works" className="hover:text-primary transition-colors">
            How It Works
          </Link>
          <Link href="/about" className="hover:text-primary transition-colors">
            About
          </Link>
        </nav>

        <div className="flex items-center gap-3">
          <Link href="/login">
            <Button variant="ghost" size="sm" className="hidden sm:inline-flex">
              <User className="w-4 h-4 mr-1.5" />
              Sign In
            </Button>
          </Link>
          <Link href="/plan/new">
            <Button variant="green" size="sm">
              <PlusCircle className="w-4 h-4 mr-1.5" />
              Start Planning
            </Button>
          </Link>
        </div>
      </div>
    </header>
  );
}

