import Link from "next/link";
import { SiteHeader } from "@/components/site-header";

export default function HomePage() {
  return (
    <>
      <SiteHeader />
      <main className="flex-1">
        {/* Hero */}
        <section className="relative overflow-hidden">
          <div
            aria-hidden
            className="absolute inset-0 bg-[radial-gradient(circle_at_30%_-10%,_rgba(91,138,114,0.10),_transparent_55%),radial-gradient(circle_at_85%_25%,_rgba(192,133,82,0.08),_transparent_50%)]"
          />
          <div className="relative mx-auto max-w-5xl px-6 pt-20 pb-24 sm:pt-28 sm:pb-32">
            <p className="text-xs uppercase tracking-[0.25em] text-stone-soft">
              For case managers, discharge planners, and the people they serve
            </p>
            <h1 className="mt-4 max-w-3xl text-balance text-5xl font-semibold leading-[1.05] tracking-tight text-stone-warm sm:text-6xl">
              Faster, better-fit housing placements.
            </h1>
            <p className="mt-6 max-w-2xl text-xl leading-relaxed text-stone-soft">
              Submit one referral. Get matched options, funding support, and
              follow-through - in minutes, not weeks.
            </p>

            <div className="mt-10 flex flex-wrap items-center gap-4">
              <Link
                href="/refer"
                className="rounded-full bg-sage px-6 py-3 text-base font-medium text-cream shadow-sm hover:bg-sage-deep transition-colors"
              >
                Refer a client
              </Link>
              <Link
                href="/login"
                className="rounded-full border border-stone-line bg-cream-50 px-6 py-3 text-base font-medium text-stone-warm hover:border-stone-soft transition-colors"
              >
                Sign in
              </Link>
            </div>

            <dl className="mt-16 grid grid-cols-1 gap-x-12 gap-y-6 sm:grid-cols-3">
              <Stat value="2-5 min" label="Submit a complete referral" />
              <Stat
                value="Top 3"
                label="Best-fit placements returned, not endless listings"
              />
              <Stat value="Same day" label="Specialist review and triage" />
            </dl>
          </div>
        </section>

        {/* Three pillars */}
        <section className="border-y border-stone-line/70 bg-cream-50">
          <div className="mx-auto max-w-5xl px-6 py-20">
            <p className="text-xs uppercase tracking-[0.25em] text-stone-soft">
              How it works
            </p>
            <h2 className="mt-3 max-w-2xl text-3xl font-semibold tracking-tight">
              Built around the workflow you already have.
            </h2>

            <div className="mt-12 grid grid-cols-1 gap-8 sm:grid-cols-3">
              <Step
                num="01"
                title="Intake"
                body="Submit the minimum we need to triage. We don't ask for SSN. We don't ask for clinical detail in a form. Phone follow-up handles the rest."
              />
              <Step
                num="02"
                title="Triage"
                body="A specialist reviews the same day. We sort independent shared housing from higher-care needs before recommending anything."
              />
              <Step
                num="03"
                title="Match"
                body="You receive 2-3 placements with a funding fit, move-in window, house rules, and the next concrete step."
              />
            </div>
          </div>
        </section>

        {/* What we sell */}
        <section className="mx-auto max-w-5xl px-6 py-24">
          <div className="grid grid-cols-1 gap-12 sm:grid-cols-2 sm:items-center">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-stone-soft">
                What we promise
              </p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight">
                Speed, confidence, and placement quality.
              </h2>
              <p className="mt-5 text-stone-soft">
                Bad fit placements destroy trust - with you, with the resident,
                and with the home. Our job is to get the fit right and stay
                with it through funding, move-in, and the months after.
              </p>
            </div>
            <ul className="space-y-4 text-stone-warm">
              <Promise text="Triage before matching - independent housing vs assisted living vs higher support" />
              <Promise text="Funding navigation - SSI, SSDI, VA, Medicaid, sponsorship, private pay" />
              <Promise text="Placement quality - house rules, accessibility, recovery environment, behavioral fit" />
              <Promise text="Post-placement support - benefits activation, ID recovery, retention follow-up" />
              <Promise text="A feedback loop - you'll know exactly where every referral stands" />
            </ul>
          </div>
        </section>

        {/* CTA */}
        <section className="bg-stone-warm text-cream">
          <div className="mx-auto max-w-5xl px-6 py-20 sm:flex sm:items-center sm:justify-between sm:gap-12">
            <div>
              <h2 className="text-3xl font-semibold tracking-tight">
                Have someone who needs housing?
              </h2>
              <p className="mt-3 text-cream/70">
                Submit your first referral. We&apos;ll show you what same-day
                placement coordination feels like.
              </p>
            </div>
            <Link
              href="/refer"
              className="mt-6 inline-flex shrink-0 rounded-full bg-cream px-6 py-3 text-base font-medium text-stone-warm hover:bg-cream-50 transition-colors sm:mt-0"
            >
              Start a referral
            </Link>
          </div>
        </section>

        <footer className="border-t border-stone-line/70 bg-cream">
          <div className="mx-auto max-w-5xl px-6 py-8 text-sm text-stone-soft sm:flex sm:items-center sm:justify-between">
            <p>Ready Rooms - Housing placement, not housing browsing.</p>
            <p className="mt-2 sm:mt-0">
              Built for vulnerable adults and the professionals supporting them.
            </p>
          </div>
        </footer>
      </main>
    </>
  );
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div>
      <dt className="text-3xl font-semibold tracking-tight text-stone-warm">
        {value}
      </dt>
      <dd className="mt-1 text-sm text-stone-soft">{label}</dd>
    </div>
  );
}

function Step({
  num,
  title,
  body,
}: {
  num: string;
  title: string;
  body: string;
}) {
  return (
    <article className="border-l-2 border-sage/40 pl-5">
      <p className="font-mono text-xs text-sage-deep">{num}</p>
      <h3 className="mt-2 text-lg font-semibold tracking-tight">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-stone-soft">{body}</p>
    </article>
  );
}

function Promise({ text }: { text: string }) {
  return (
    <li className="flex items-start gap-3">
      <span
        aria-hidden
        className="mt-1.5 inline-block h-1.5 w-1.5 shrink-0 rounded-full bg-sage"
      />
      <span>{text}</span>
    </li>
  );
}
