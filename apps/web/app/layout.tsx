import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Ready Rooms — Faster, better-fit housing placements",
  description:
    "Submit a referral. Get matched options, funding support, and follow-through. Built for case managers, discharge planners, and the people they serve.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full`}>
      <body className="min-h-full flex flex-col bg-cream text-stone-warm antialiased">
        {children}
      </body>
    </html>
  );
}
