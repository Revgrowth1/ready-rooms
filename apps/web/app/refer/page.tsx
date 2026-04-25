import { SiteHeader } from "@/components/site-header";
import { IntakeForm } from "./intake-form";

export const metadata = {
  title: "Refer a client - Ready Rooms",
};

export default function ReferPage() {
  return (
    <>
      <SiteHeader />
      <main className="flex-1">
        <div className="mx-auto max-w-3xl px-6 py-12">
          <header className="mb-10">
            <p className="text-xs uppercase tracking-[0.2em] text-stone-soft">
              New referral
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight">
              Refer a client
            </h1>
            <p className="mt-3 max-w-prose text-stone-soft">
              Two minutes. We&apos;ll review same-day, return the best 2-3 placement
              options, and follow up by your preferred channel.
            </p>
          </header>

          <div className="rounded-2xl border border-stone-line bg-cream-50 p-8 shadow-sm">
            <IntakeForm />
          </div>
        </div>
      </main>
    </>
  );
}
