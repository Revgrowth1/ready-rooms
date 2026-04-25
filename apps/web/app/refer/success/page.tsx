import Link from "next/link";
import { SiteHeader } from "@/components/site-header";

export const metadata = {
  title: "Referral received - Ready Rooms",
};

export default async function ReferSuccessPage({
  searchParams,
}: {
  searchParams: Promise<{ id?: string }>;
}) {
  const { id } = await searchParams;

  return (
    <>
      <SiteHeader />
      <main className="flex flex-1 items-center justify-center px-6 py-16">
        <div className="w-full max-w-lg text-center">
          <div className="mx-auto mb-6 flex h-12 w-12 items-center justify-center rounded-full bg-sage-soft text-sage-deep">
            <svg
              aria-hidden
              viewBox="0 0 24 24"
              fill="none"
              className="h-6 w-6"
              stroke="currentColor"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M5 12l5 5L20 7" />
            </svg>
          </div>
          <p className="text-xs uppercase tracking-[0.2em] text-stone-soft">
            Referral received
          </p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight">
            Thank you - we&apos;ve got it from here.
          </h1>
          <p className="mt-4 text-stone-soft">
            A Ready Rooms specialist is reviewing your submission and will
            return the strongest placement matches with funding fit and a
            move-in window.
          </p>
          {id ? (
            <p className="mt-6 text-sm text-stone-soft">
              Reference: <span className="font-mono text-stone-warm">{id}</span>
            </p>
          ) : null}

          <div className="mt-10 flex items-center justify-center gap-4">
            <Link
              href="/refer"
              className="rounded-md border border-stone-line bg-cream-50 px-4 py-2 text-sm font-medium text-stone-warm hover:border-stone-soft transition-colors"
            >
              Refer another client
            </Link>
          </div>
        </div>
      </main>
    </>
  );
}
