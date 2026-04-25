import { ReactNode } from "react";

interface FieldProps {
  label: string;
  htmlFor: string;
  hint?: string;
  required?: boolean;
  children: ReactNode;
}

export function Field({ label, htmlFor, hint, required, children }: FieldProps) {
  return (
    <div className="space-y-1.5">
      <label
        htmlFor={htmlFor}
        className="block text-sm font-medium text-stone-warm"
      >
        {label}
        {required ? <span className="ml-1 text-error">*</span> : null}
      </label>
      {children}
      {hint ? <p className="text-xs text-stone-soft">{hint}</p> : null}
    </div>
  );
}

const inputBase =
  "block w-full rounded-md border border-stone-line bg-cream-50 px-3 py-2 text-stone-warm placeholder:text-stone-soft/70 shadow-sm focus:border-brand-blue focus:outline-none focus:ring-2 focus:ring-brand-blue/30 transition";

export function TextInput(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={`${inputBase} ${props.className ?? ""}`} />;
}

export function TextArea(
  props: React.TextareaHTMLAttributes<HTMLTextAreaElement>,
) {
  return (
    <textarea
      {...props}
      className={`${inputBase} min-h-[120px] ${props.className ?? ""}`}
    />
  );
}

export function Select(
  props: React.SelectHTMLAttributes<HTMLSelectElement> & { children: ReactNode },
) {
  const { children, ...rest } = props;
  return (
    <select {...rest} className={`${inputBase} ${props.className ?? ""}`}>
      {children}
    </select>
  );
}
