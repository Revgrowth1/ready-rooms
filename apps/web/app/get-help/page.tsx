import Link from "next/link";
import { SiteHeader } from "@/components/site-header";

export const metadata = {
  title: "Find housing - Ready Rooms",
};

export default function GetHelpPage() {
  return (
    <>
      <SiteHeader />
      <main className="flex-1">
        <div className="mx-auto max-w-3xl px-6 py-16">
          <p className="text-xs font-medium uppercase tracking-[0.25em] text-brand-orange-deep">
            For individuals &amp; families
          </p>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight">
            Let&apos;s find you a place to land.
          </h1>
          <p className="mt-4 max-w-2xl text-lg text-stone-soft">
            Tell us a little about your situation. A Ready Rooms specialist
            will reach out within 24 hours - by phone, text, or email - to walk
            you through what&apos;s possible.
          </p>

          <div className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <ContactCard
              eyebrow="Email"
              value="info@ReadyRooms.org"
              href="mailto:info@ReadyRooms.org"
              body="Best for sharing details or attaching documents. We respond same business day."
            />
            <ContactCard
              eyebrow="Phone &amp; text"
              value="Coming soon"
              href="mailto:info@ReadyRooms.org?subject=Request%20a%20call"
              body="Rolling out a phone line in the next few weeks. Email us in the meantime and we&apos;ll call you back."
            />
          </div>

          <section className="mt-14 rounded-2xl border border-cream-line bg-brand-blue-pale p-8">
            <h2 className="text-lg font-semibold">What to include in your message</h2>
            <ul className="mt-4 space-y-3 text-stone-warm">
              <Tip text="Your name and a phone number or email we can reach you on" />
              <Tip text="The city or area you're hoping to live in" />
              <Tip text="When you need to move (today, this week, this month, flexible)" />
              <Tip text="Any income or benefits you're working with (SSI, SSDI, VA, Medicaid, private pay) - just what you know" />
              <Tip text="Anything else that would help us find the right fit (mobility, recovery, family, etc.)" />
            </ul>
            <p className="mt-6 text-sm text-stone-soft">
              You don&apos;t need to share medical or treatment details by email.
              We&apos;ll cover those on a phone call where it&apos;s safer.
            </p>
          </section>

          <p className="mt-12 text-sm text-stone-soft">
            Are you a case manager, social worker, or discharge planner helping
            someone find housing?{" "}
            <Link href="/refer" className="text-brand-blue-deep hover:underline">
              Use the professional referral form &rarr;
            </Link>
          </p>
        </div>
      </main>
    </>
  );
}

function ContactCard({
  eyebrow,
  value,
  href,
  body,
}: {
  eyebrow: string;
  value: string;
  href: string;
  body: string;
}) {
  return (
    <a
      href={href}
      className="group block rounded-2xl border border-cream-line bg-cream-50 p-6 hover:border-brand-orange hover:shadow-md transition-all"
    >
      <p
        className="text-xs font-medium uppercase tracking-[0.18em] text-brand-orange-deep"
        dangerouslySetInnerHTML={{ __html: eyebrow }}
      />
      <p className="mt-2 text-xl font-semibold tracking-tight text-stone-warm group-hover:text-brand-orange-deep transition-colors">
        {value}
      </p>
      <p className="mt-3 text-sm text-stone-soft">{body}</p>
    </a>
  );
}

function Tip({ text }: { text: string }) {
  return (
    <li className="flex items-start gap-3">
      <span
        aria-hidden
        className="mt-1.5 inline-block h-1.5 w-1.5 shrink-0 rounded-full bg-brand-blue"
      />
      <span>{text}</span>
    </li>
  );
}
