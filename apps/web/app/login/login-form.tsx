"use client";

import { useActionState } from "react";
import { signIn, type SignInState } from "./actions";
import { Field, TextInput } from "@/components/field";

export function LoginForm({ next }: { next: string }) {
  const [state, formAction, pending] = useActionState<
    SignInState | undefined,
    FormData
  >(signIn, undefined);

  return (
    <form action={formAction} className="space-y-5">
      <input type="hidden" name="next" value={next} />
      <Field
        label="Work email"
        htmlFor="email"
        required
        hint="We'll send a one-time link. No password required."
      >
        <TextInput
          id="email"
          name="email"
          type="email"
          autoComplete="email"
          required
          placeholder="you@yourorganization.org"
          defaultValue={state?.email ?? ""}
        />
      </Field>

      <button
        type="submit"
        disabled={pending}
        className="w-full rounded-md bg-brand-blue px-4 py-2.5 font-medium text-cream shadow-sm hover:bg-brand-blue-deep disabled:opacity-60 transition-colors"
      >
        {pending ? "Sending link..." : "Send sign-in link"}
      </button>

      {state?.message ? (
        <p
          className={`text-sm ${
            state.message.startsWith("Check") ? "text-brand-blue-deep" : "text-error"
          }`}
        >
          {state.message}
        </p>
      ) : null}
    </form>
  );
}
