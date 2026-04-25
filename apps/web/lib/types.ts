export type UserRole = "admin" | "case_manager";

export type IntakeStatus =
  | "new"
  | "reviewing"
  | "matched"
  | "placed"
  | "closed";

export type Urgency =
  | "immediate"
  | "this_week"
  | "this_month"
  | "flexible";

export type FundingSource =
  | "ssi"
  | "ssdi"
  | "va"
  | "medicaid"
  | "private_pay"
  | "nonprofit_sponsorship"
  | "other";

export type HousingNeed =
  | "independent_shared"
  | "assisted_living"
  | "higher_support"
  | "triage_needed";

export interface Profile {
  id: string;
  email: string;
  full_name: string | null;
  org_name: string | null;
  role: UserRole;
  created_at: string;
  updated_at: string;
}

export interface Intake {
  id: string;
  case_manager_id: string;

  client_first_name: string;
  client_last_name: string;
  client_dob_year: number | null;
  client_phone: string | null;
  client_email: string | null;

  referral_source_org: string;
  referral_source_role: string | null;

  preferred_city: string;
  preferred_state: string;
  urgency: Urgency;

  funding_source: FundingSource;
  monthly_income_cents: number | null;

  housing_need: HousingNeed;

  notes: string | null;
  status: IntakeStatus;

  created_at: string;
  updated_at: string;
}

export const URGENCY_LABELS: Record<Urgency, string> = {
  immediate: "Immediate (within 48 hours)",
  this_week: "This week",
  this_month: "This month",
  flexible: "Flexible",
};

export const FUNDING_LABELS: Record<FundingSource, string> = {
  ssi: "SSI",
  ssdi: "SSDI",
  va: "VA benefits",
  medicaid: "Medicaid",
  private_pay: "Private pay",
  nonprofit_sponsorship: "Nonprofit sponsorship",
  other: "Other / unsure",
};

export const HOUSING_NEED_LABELS: Record<HousingNeed, string> = {
  independent_shared: "Independent shared housing",
  assisted_living: "Assisted living",
  higher_support: "Higher-support setting",
  triage_needed: "Needs assessment",
};

export const STATUS_LABELS: Record<IntakeStatus, string> = {
  new: "New",
  reviewing: "Reviewing",
  matched: "Matched",
  placed: "Placed",
  closed: "Closed",
};
