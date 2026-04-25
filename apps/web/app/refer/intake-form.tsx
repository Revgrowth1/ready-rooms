"use client";

import { useActionState } from "react";
import { createIntake, type IntakeState } from "./actions";
import { Field, TextInput, TextArea, Select } from "@/components/field";
import {
  URGENCY_LABELS,
  FUNDING_LABELS,
  HOUSING_NEED_LABELS,
} from "@/lib/types";

export function IntakeForm() {
  const [state, formAction, pending] = useActionState<
    IntakeState | undefined,
    FormData
  >(createIntake, undefined);

  const err = (key: string) => state?.fieldErrors?.[key];

  return (
    <form action={formAction} className="space-y-10">
      {/* Section 1: client */}
      <section className="space-y-5">
        <header>
          <h2 className="text-lg font-semibold">Client</h2>
          <p className="text-sm text-stone-soft">
            Minimum identifying info. We don&apos;t store SSN or full date of birth.
          </p>
        </header>

        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
          <Field label="First name" htmlFor="client_first_name" required>
            <TextInput
              id="client_first_name"
              name="client_first_name"
              required
              autoComplete="off"
            />
            {err("client_first_name") && (
              <p className="text-xs text-error">{err("client_first_name")}</p>
            )}
          </Field>
          <Field label="Last name" htmlFor="client_last_name" required>
            <TextInput
              id="client_last_name"
              name="client_last_name"
              required
              autoComplete="off"
            />
            {err("client_last_name") && (
              <p className="text-xs text-error">{err("client_last_name")}</p>
            )}
          </Field>

          <Field
            label="Year of birth"
            htmlFor="client_dob_year"
            hint="Year only, e.g. 1968"
          >
            <TextInput
              id="client_dob_year"
              name="client_dob_year"
              type="number"
              min={1900}
              max={2100}
              placeholder="1968"
            />
            {err("client_dob_year") && (
              <p className="text-xs text-error">{err("client_dob_year")}</p>
            )}
          </Field>

          <Field label="Client phone" htmlFor="client_phone">
            <TextInput
              id="client_phone"
              name="client_phone"
              type="tel"
              autoComplete="off"
              placeholder="(555) 555-1234"
            />
          </Field>

          <Field
            label="Client email"
            htmlFor="client_email"
            hint="Optional. We'll never email the client without your go-ahead."
          >
            <TextInput
              id="client_email"
              name="client_email"
              type="email"
              autoComplete="off"
            />
          </Field>
        </div>
      </section>

      {/* Section 2: referral source */}
      <section className="space-y-5">
        <header>
          <h2 className="text-lg font-semibold">You</h2>
          <p className="text-sm text-stone-soft">
            So we know who to follow up with.
          </p>
        </header>

        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
          <Field
            label="Referring organization"
            htmlFor="referral_source_org"
            required
          >
            <TextInput
              id="referral_source_org"
              name="referral_source_org"
              required
              placeholder="e.g. St. Vincent Discharge Planning"
            />
            {err("referral_source_org") && (
              <p className="text-xs text-error">{err("referral_source_org")}</p>
            )}
          </Field>

          <Field label="Your role" htmlFor="referral_source_role">
            <TextInput
              id="referral_source_role"
              name="referral_source_role"
              placeholder="e.g. Discharge planner"
            />
          </Field>
        </div>
      </section>

      {/* Section 3: placement */}
      <section className="space-y-5">
        <header>
          <h2 className="text-lg font-semibold">Placement</h2>
          <p className="text-sm text-stone-soft">
            Where they want to live and how soon.
          </p>
        </header>

        <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
          <Field label="Preferred city" htmlFor="preferred_city" required>
            <TextInput
              id="preferred_city"
              name="preferred_city"
              required
              placeholder="Houston"
            />
            {err("preferred_city") && (
              <p className="text-xs text-error">{err("preferred_city")}</p>
            )}
          </Field>

          <Field label="State" htmlFor="preferred_state" required>
            <TextInput
              id="preferred_state"
              name="preferred_state"
              required
              maxLength={2}
              placeholder="TX"
              className="uppercase"
            />
            {err("preferred_state") && (
              <p className="text-xs text-error">{err("preferred_state")}</p>
            )}
          </Field>

          <Field label="Urgency" htmlFor="urgency">
            <Select id="urgency" name="urgency" defaultValue="this_week">
              {Object.entries(URGENCY_LABELS).map(([k, v]) => (
                <option key={k} value={k}>
                  {v}
                </option>
              ))}
            </Select>
          </Field>

          <Field label="Funding source" htmlFor="funding_source">
            <Select
              id="funding_source"
              name="funding_source"
              defaultValue="other"
            >
              {Object.entries(FUNDING_LABELS).map(([k, v]) => (
                <option key={k} value={k}>
                  {v}
                </option>
              ))}
            </Select>
          </Field>

          <Field
            label="Monthly income"
            htmlFor="monthly_income"
            hint="Optional. USD."
          >
            <TextInput
              id="monthly_income"
              name="monthly_income"
              type="number"
              min={0}
              step={1}
              placeholder="943"
            />
            {err("monthly_income") && (
              <p className="text-xs text-error">{err("monthly_income")}</p>
            )}
          </Field>

          <Field
            label="Housing need"
            htmlFor="housing_need"
            hint="Best guess - we'll triage."
          >
            <Select
              id="housing_need"
              name="housing_need"
              defaultValue="triage_needed"
            >
              {Object.entries(HOUSING_NEED_LABELS).map(([k, v]) => (
                <option key={k} value={k}>
                  {v}
                </option>
              ))}
            </Select>
          </Field>
        </div>

        <Field
          label="Notes"
          htmlFor="notes"
          hint="Anything that would help us match well: behavior, ADL support, transportation, fit considerations."
        >
          <TextArea
            id="notes"
            name="notes"
            rows={5}
            placeholder="Share what would help us find the right fit. Avoid sharing detailed clinical or substance-use records here."
          />
        </Field>
      </section>

      {state?.message ? (
        <div className="rounded-md border border-error/40 bg-error/5 px-4 py-3 text-sm text-error">
          {state.message}
        </div>
      ) : null}

      <div className="flex items-center justify-between gap-4 border-t border-stone-line pt-6">
        <p className="text-xs text-stone-soft">
          We collect only what we need to screen and match. Health and
          treatment specifics belong in a follow-up phone call.
        </p>
        <button
          type="submit"
          disabled={pending}
          className="shrink-0 rounded-md bg-brand-blue px-5 py-2.5 font-medium text-cream shadow-sm hover:bg-brand-blue-deep disabled:opacity-60 transition-colors"
        >
          {pending ? "Submitting..." : "Submit referral"}
        </button>
      </div>
    </form>
  );
}
