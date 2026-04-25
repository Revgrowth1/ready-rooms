import Link from "next/link";
import { createClient } from "@/lib/supabase/server";
import {
  STATUS_LABELS,
  URGENCY_LABELS,
  HOUSING_NEED_LABELS,
  type Intake,
} from "@/lib/types";

export const metadata = {
  title: "Admin - Ready Rooms",
};

export const dynamic = "force-dynamic";

export default async function AdminPage() {
  const supabase = await createClient();
  const { data: intakes } = await supabase
    .from("intakes")
    .select("*")
    .order("created_at", { ascending: false });

  const list = (intakes ?? []) as Intake[];

  const counts = list.reduce(
    (acc, i) => {
      acc[i.status] = (acc[i.status] ?? 0) + 1;
      return acc;
    },
    {} as Record<string, number>,
  );

  return (
    <main className="flex-1">
      <div className="mx-auto max-w-6xl px-6 py-12">
        <header className="mb-8 flex items-end justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-stone-soft">
              Admin
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight">
              Active referrals
            </h1>
            <p className="mt-2 text-stone-soft">
              {list.length} total - {counts.new ?? 0} new -{" "}
              {counts.reviewing ?? 0} reviewing - {counts.matched ?? 0} matched
            </p>
          </div>
          <Link
            href="/refer"
            className="rounded-md border border-stone-line bg-cream-50 px-4 py-2 text-sm font-medium text-stone-warm hover:border-stone-soft transition-colors"
          >
            New referral
          </Link>
        </header>

        {list.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-stone-line bg-cream-50 px-6 py-16 text-center">
            <p className="text-stone-soft">
              No referrals yet. Submit one from the{" "}
              <Link href="/refer" className="text-sage-deep hover:underline">
                referral form
              </Link>
              .
            </p>
          </div>
        ) : (
          <div className="overflow-hidden rounded-2xl border border-stone-line bg-cream-50 shadow-sm">
            <table className="w-full text-sm">
              <thead className="border-b border-stone-line bg-cream text-left text-xs uppercase tracking-wider text-stone-soft">
                <tr>
                  <th className="px-4 py-3 font-medium">Submitted</th>
                  <th className="px-4 py-3 font-medium">Client</th>
                  <th className="px-4 py-3 font-medium">Location</th>
                  <th className="px-4 py-3 font-medium">Urgency</th>
                  <th className="px-4 py-3 font-medium">Need</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody>
                {list.map((i) => (
                  <tr
                    key={i.id}
                    className="border-b border-stone-line/60 last:border-0 hover:bg-cream"
                  >
                    <td className="px-4 py-3 text-stone-soft">
                      {new Date(i.created_at).toLocaleDateString(undefined, {
                        month: "short",
                        day: "numeric",
                      })}
                    </td>
                    <td className="px-4 py-3">
                      <div className="font-medium text-stone-warm">
                        {i.client_first_name} {i.client_last_name}
                      </div>
                      <div className="text-xs text-stone-soft">
                        from {i.referral_source_org}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-stone-soft">
                      {i.preferred_city}, {i.preferred_state}
                    </td>
                    <td className="px-4 py-3 text-stone-soft">
                      {URGENCY_LABELS[i.urgency]}
                    </td>
                    <td className="px-4 py-3 text-stone-soft">
                      {HOUSING_NEED_LABELS[i.housing_need]}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={i.status} />
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Link
                        href={`/admin/${i.id}`}
                        className="text-sage-deep hover:underline"
                      >
                        Open &rarr;
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </main>
  );
}

function StatusBadge({ status }: { status: keyof typeof STATUS_LABELS }) {
  const styles: Record<string, string> = {
    new: "bg-amber-warm/15 text-amber-warm",
    reviewing: "bg-sage-soft text-sage-deep",
    matched: "bg-sage text-cream",
    placed: "bg-sage-deep text-cream",
    closed: "bg-stone-line text-stone-soft",
  };
  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${
        styles[status] ?? "bg-stone-line text-stone-soft"
      }`}
    >
      {STATUS_LABELS[status]}
    </span>
  );
}
