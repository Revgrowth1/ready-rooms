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
            className="absolute inset-0 bg-[radial-gradient(circle_at_85%_-10%,_rgba(232,130,57,0.18),_transparent_50%),radial-gradient(circle_at_15%_30%,_rgba(40,118,200,0.10),_transparent_55%)]"
          />
          <div className="relative mx-auto max-w-5xl px-6 pt-20 pb-24 sm:pt-28 sm:pb-32">
            <p className="text-xs font-medium uppercase tracking-[0.25em] text-brand-blue-deep">
              Nationwide housing assistance
            </p>
            <h1 className="mt-4 max-w-3xl text-balance text-5xl font-semibold leading-[1.05] tracking-tight text-stone-warm sm:text-6xl">
              A safe place to live, ready when you need it.
            </h1>
            <p className="mt-6 max-w-2xl text-xl leading-relaxed text-stone-soft">
              Whether you&apos;re helping someone find housing or looking for a
              place yourself, Ready Rooms matches people with transitional and
              independent living homes across the country - usually within days.
            </p>

            {/* Two doors */}
            <div className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Link
                href="/refer"
                className="group rounded-2xl border border-stone-line bg-cream-50 p-6 hover:border-brand-blue hover:shadow-md transition-all"
              >
                <p className="text-xs font-medium uppercase tracking-[0.18em] text-brand-blue-deep">
                  For social workers, hospitals, case managers
                </p>
                <h2 className="mt-3 text-2xl font-semibold tracking-tight text-stone-warm">
                  Refer a client
                </h2>
                <p className="mt-2 text-sm text-stone-soft">
                  Submit one referral - we send back the best 2-3 placement
                  options with funding fit and next steps.
                </p>
                <span className="mt-4 inline-flex items-center text-sm font-medium text-brand-blue-deep group-hover:underline">
                  Start a referral &rarr;
                </span>
              </Link>

              <Link
                href="/get-help"
                className="group rounded-2xl border border-stone-line bg-cream-50 p-6 hover:border-brand-orange hover:shadow-md transition-all"
              >
                <p className="text-xs font-medium uppercase tracking-[0.18em] text-brand-orange-deep">
                  For individuals &amp; families
                </p>
                <h2 className="mt-3 text-2xl font-semibold tracking-tight text-stone-warm">
                  Find housing for me
                </h2>
                <p className="mt-2 text-sm text-stone-soft">
                  Whether you&apos;re a veteran, exiting treatment, or helping a
                  loved one - we&apos;ll guide you through every step.
                </p>
                <span className="mt-4 inline-flex items-center text-sm font-medium text-brand-orange-deep group-hover:underline">
                  Get housing help &rarr;
                </span>
              </Link>
            </div>

            <p className="mt-10 text-sm text-stone-soft">
              Or call{" "}
              <a
                href="mailto:info@ReadyRooms.org"
                className="font-medium text-stone-warm hover:text-brand-blue-deep"
              >
                info@ReadyRooms.org
              </a>{" "}
              and a specialist will reach out the same day.
            </p>
          </div>
        </section>

        {/* Who we help */}
        <section className="border-y border-cream-line bg-brand-blue-pale">
          <div className="mx-auto max-w-5xl px-6 py-16">
            <div className="max-w-2xl">
              <p className="text-xs font-medium uppercase tracking-[0.25em] text-brand-blue-deep">
                Who we help
              </p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight">
                Built for people who need somewhere to land.
              </h2>
            </div>

            <ul className="mt-10 grid grid-cols-2 gap-x-6 gap-y-4 sm:grid-cols-3">
              <Audience icon="◇" label="Veterans" />
              <Audience icon="◇" label="People exiting incarceration" />
              <Audience icon="◇" label="People exiting treatment or recovery" />
              <Audience icon="◇" label="Seniors on fixed income" />
              <Audience icon="◇" label="Families helping a loved one" />
              <Audience icon="◇" label="Anyone needing a fresh start" />
            </ul>
          </div>
        </section>

        {/* How it works */}
        <section className="mx-auto max-w-5xl px-6 py-24">
          <div className="max-w-2xl">
            <p className="text-xs font-medium uppercase tracking-[0.25em] text-brand-blue-deep">
              How it works
            </p>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight">
              Three simple steps. Real human support at every one.
            </h2>
          </div>

          <div className="mt-12 grid grid-cols-1 gap-8 sm:grid-cols-3">
            <Step
              num="01"
              title="Tell us who needs housing"
              body="A short form: who they are, where they want to live, what they can afford. No SSN. No clinical detail."
            />
            <Step
              num="02"
              title="We review the same day"
              body="A specialist reviews and figures out whether shared housing, assisted living, or higher support is the right fit."
            />
            <Step
              num="03"
              title="Pick from the best options"
              body="You see 2-3 strong matches with photos, funding fit, house rules, and a move-in window. Choose. Move in."
            />
          </div>
        </section>

        {/* What we promise */}
        <section className="bg-brand-orange-soft/40">
          <div className="mx-auto max-w-5xl px-6 py-20">
            <div className="grid grid-cols-1 gap-12 sm:grid-cols-2 sm:items-center">
              <div>
                <p className="text-xs font-medium uppercase tracking-[0.25em] text-brand-orange-deep">
                  What we cover
                </p>
                <h2 className="mt-3 text-3xl font-semibold tracking-tight">
                  We don&apos;t stop at the front door.
                </h2>
                <p className="mt-5 text-stone-soft">
                  Real housing stability is more than a bed. We help with the
                  things that keep people housed: benefits, ID, transportation,
                  and a check-in cadence so nobody falls through the cracks.
                </p>
              </div>
              <ul className="space-y-4 text-stone-warm">
                <Promise text="Triage first - shared housing vs assisted living vs higher support" />
                <Promise text="Funding navigation - SSI, SSDI, VA, Medicaid, sponsorship, private pay" />
                <Promise text="Quality housing - vetted homes, house rules clear up front" />
                <Promise text="Post-placement support - ID, benefits, transportation, follow-up" />
                <Promise text="A specialist you can reach - by phone, email, or text" />
              </ul>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="bg-stone-warm text-cream">
          <div className="mx-auto max-w-5xl px-6 py-20 sm:flex sm:items-center sm:justify-between sm:gap-12">
            <div>
              <h2 className="text-3xl font-semibold tracking-tight text-cream">
                Ready when you are.
              </h2>
              <p className="mt-3 text-cream/70">
                Submit a referral or ask for help - we&apos;ll take it from
                here.
              </p>
            </div>
            <div className="mt-6 flex flex-wrap items-center gap-3 sm:mt-0">
              <Link
                href="/refer"
                className="inline-flex shrink-0 rounded-full bg-brand-blue px-6 py-3 text-base font-medium text-cream shadow-sm hover:bg-brand-blue-deep transition-colors"
              >
                Refer a client
              </Link>
              <Link
                href="/get-help"
                className="inline-flex shrink-0 rounded-full border border-cream/30 bg-transparent px-6 py-3 text-base font-medium text-cream hover:bg-cream/10 transition-colors"
              >
                Find housing
              </Link>
            </div>
          </div>
        </section>

        <footer className="border-t border-cream-line bg-cream">
          <div className="mx-auto max-w-5xl px-6 py-10 text-sm text-stone-soft">
            <div className="sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-stone-warm font-medium">
                  <span className="text-brand-orange">Ready</span>{" "}
                  <span className="text-brand-blue">Rooms</span>
                </p>
                <p className="mt-1 text-xs">
                  Nationwide housing assistance for transitional &amp;
                  independent living.
                </p>
              </div>
              <div className="mt-4 flex flex-wrap items-center gap-x-6 gap-y-2 sm:mt-0">
                <a
                  href="mailto:info@ReadyRooms.org"
                  className="hover:text-brand-blue-deep"
                >
                  info@ReadyRooms.org
                </a>
                <Link href="/refer" className="hover:text-brand-blue-deep">
                  Refer a client
                </Link>
                <Link href="/get-help" className="hover:text-brand-orange-deep">
                  Find housing
                </Link>
              </div>
            </div>
          </div>
        </footer>
      </main>
    </>
  );
}

function Audience({ icon, label }: { icon: string; label: string }) {
  return (
    <li className="flex items-start gap-2 text-stone-warm">
      <span aria-hidden className="mt-0.5 text-brand-blue">
        {icon}
      </span>
      <span>{label}</span>
    </li>
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
    <article className="border-l-2 border-brand-blue/30 pl-5">
      <p className="font-mono text-xs font-medium text-brand-blue-deep">{num}</p>
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
        className="mt-1.5 inline-block h-1.5 w-1.5 shrink-0 rounded-full bg-brand-orange"
      />
      <span>{text}</span>
    </li>
  );
}
