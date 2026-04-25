import Link from "next/link";
import { notFound } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import {
  STATUS_LABELS,
  URGENCY_LABELS,
  FUNDING_LABELS,
  HOUSING_NEED_LABELS,
  type Intake,
} from "@/lib/types";
import { updateStatus } from "./actions";

export const dynamic = "force-dynamic";

export default async function IntakeDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const supabase = await createClient();

  const { data: intake } = await supabase
    .from("intakes")
    .select("*")
    .eq("id", id)
    .maybeSingle();

  if (!intake) notFound();

  const i = intake as Intake;

  const submittedBy = await supabase
    .from("profiles")
    .select("email, full_name, org_name")
    .eq("id", i.case_manager_id)
    .maybeSingle();

  return (
    <main className="flex-1">
      <div className="mx-auto max-w-3xl px-6 py-12">
        <Link
          href="/admin"
          className="text-sm text-stone-soft hover:text-stone-warm"
        >
          &larr; All referrals
        </Link>

        <header className="mt-4 mb-8 flex items-start justify-between gap-6">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-stone-soft">
              Referral
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight">
              {i.client_first_name} {i.client_last_name}
            </h1>
            <p className="mt-2 text-stone-soft">
              Submitted{" "}
              {new Date(i.created_at).toLocaleString(undefined, {
                dateStyle: "medium",
                timeStyle: "short",
              })}{" "}
              by {submittedBy.data?.email ?? "unknown"}
              {submittedBy.data?.org_name
                ? ` (${submittedBy.data.org_name})`
                : ""}
            </p>
          </div>

          <form action={updateStatus} className="flex items-center gap-2">
            <input type="hidden" name="id" value={i.id} />
            <label htmlFor="status" className="sr-only">
              Status
            </label>
            <select
              id="status"
              name="status"
              defaultValue={i.status}
              className="rounded-md border border-stone-line bg-cream-50 px-3 py-2 text-sm focus:border-brand-blue focus:outline-none focus:ring-2 focus:ring-brand-blue/30"
            >
              {Object.entries(STATUS_LABELS).map(([k, v]) => (
                <option key={k} value={k}>
                  {v}
                </option>
              ))}
            </select>
            <button
              type="submit"
              className="rounded-md bg-brand-blue px-3 py-2 text-sm font-medium text-cream hover:bg-brand-blue-deep transition-colors"
            >
              Update
            </button>
          </form>
        </header>

        <div className="space-y-8">
          <Card title="Client">
            <Row label="Name">
              {i.client_first_name} {i.client_last_name}
            </Row>
            <Row label="Year of birth">{i.client_dob_year ?? "—"}</Row>
            <Row label="Phone">{i.client_phone ?? "—"}</Row>
            <Row label="Email">{i.client_email ?? "—"}</Row>
          </Card>

          <Card title="Referral source">
            <Row label="Organization">{i.referral_source_org}</Row>
            <Row label="Role">{i.referral_source_role ?? "—"}</Row>
          </Card>

          <Card title="Placement">
            <Row label="Location">
              {i.preferred_city}, {i.preferred_state}
            </Row>
            <Row label="Urgency">{URGENCY_LABELS[i.urgency]}</Row>
            <Row label="Funding">{FUNDING_LABELS[i.funding_source]}</Row>
            <Row label="Monthly income">
              {i.monthly_income_cents != null
                ? `$${(i.monthly_income_cents / 100).toLocaleString()}`
                : "—"}
            </Row>
            <Row label="Housing need">{HOUSING_NEED_LABELS[i.housing_need]}</Row>
          </Card>

          {i.notes ? (
            <Card title="Notes">
              <p className="whitespace-pre-wrap text-stone-warm">{i.notes}</p>
            </Card>
          ) : null}
        </div>
      </div>
    </main>
  );
}

function Card({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-2xl border border-stone-line bg-cream-50 p-6 shadow-sm">
      <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-stone-soft">
        {title}
      </h2>
      <div className="space-y-3 text-sm">{children}</div>
    </section>
  );
}

function Row({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="grid grid-cols-3 gap-4">
      <dt className="text-stone-soft">{label}</dt>
      <dd className="col-span-2 text-stone-warm">{children}</dd>
    </div>
  );
}
