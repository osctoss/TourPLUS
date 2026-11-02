import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";

export const metadata: Metadata = {
  title: "TourPlus AI — Patient-Centric Medical Tourism in India",
  description:
    "AI-assisted decision-support platform connecting hospital discovery, transparent budgeting, recovery-aware tourism, and travel agency package matching.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Montserrat:wght@600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen flex flex-col bg-white text-body font-sans antialiased">
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}

