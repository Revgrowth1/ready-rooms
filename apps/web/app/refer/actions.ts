"use server";

import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";

export interface IntakeState {
  message?: string;
  fieldErrors?: Record<string, string>;
}

const REQUIRED = [
  "client_first_name",
  "client_last_name",
  "referral_source_org",
  "preferred_city",
  "preferred_state",
];

export async function createIntake(
  _prevState: IntakeState | undefined,
  formData: FormData,
): Promise<IntakeState> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return { message: "You must be signed in to submit a referral." };
  }

  const fieldErrors: Record<string, string> = {};
  for (const key of REQUIRED) {
    const v = String(formData.get(key) ?? "").trim();
    if (!v) fieldErrors[key] = "Required";
  }

  const dobYearRaw = String(formData.get("client_dob_year") ?? "").trim();
  let client_dob_year: number | null = null;
  if (dobYearRaw) {
    const parsed = Number.parseInt(dobYearRaw, 10);
    if (Number.isNaN(parsed) || parsed < 1900 || parsed > 2100) {
      fieldErrors.client_dob_year = "Use a 4-digit year";
    } else {
      client_dob_year = parsed;
    }
  }

  const monthlyIncomeRaw = String(
    formData.get("monthly_income") ?? "",
  ).trim();
  let monthly_income_cents: number | null = null;
  if (monthlyIncomeRaw) {
    const parsed = Number.parseFloat(monthlyIncomeRaw);
    if (Number.isNaN(parsed) || parsed < 0) {
      fieldErrors.monthly_income = "Use a positive number";
    } else {
      monthly_income_cents = Math.round(parsed * 100);
    }
  }

  if (Object.keys(fieldErrors).length > 0) {
    return {
      message: "Please correct the highlighted fields.",
      fieldErrors,
    };
  }

  const insertPayload = {
    case_manager_id: user.id,
    client_first_name: String(formData.get("client_first_name")).trim(),
    client_last_name: String(formData.get("client_last_name")).trim(),
    client_dob_year,
    client_phone: stringOrNull(formData.get("client_phone")),
    client_email: stringOrNull(formData.get("client_email")),
    referral_source_org: String(formData.get("referral_source_org")).trim(),
    referral_source_role: stringOrNull(formData.get("referral_source_role")),
    preferred_city: String(formData.get("preferred_city")).trim(),
    preferred_state: String(formData.get("preferred_state"))
      .trim()
      .toUpperCase()
      .slice(0, 2),
    urgency: String(formData.get("urgency") ?? "this_week"),
    funding_source: String(formData.get("funding_source") ?? "other"),
    monthly_income_cents,
    housing_need: String(formData.get("housing_need") ?? "triage_needed"),
    notes: stringOrNull(formData.get("notes")),
  };

  const { data, error } = await supabase
    .from("intakes")
    .insert(insertPayload)
    .select("id")
    .single();

  if (error) {
    return { message: `Could not save referral: ${error.message}` };
  }

  revalidatePath("/admin");
  redirect(`/refer/success?id=${data.id}`);
}

function stringOrNull(v: FormDataEntryValue | null): string | null {
  if (v === null) return null;
  const s = String(v).trim();
  return s ? s : null;
}
