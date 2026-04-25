import Link from "next/link";
import { LoginForm } from "./login-form";
import { SiteHeader } from "@/components/site-header";

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ next?: string }>;
}) {
  const { next = "/refer" } = await searchParams;

  return (
    <>
      <SiteHeader />
      <main className="flex flex-1 items-center justify-center px-6 py-16">
        <div className="w-full max-w-md">
          <div className="mb-8 text-center">
            <p className="text-xs uppercase tracking-[0.2em] text-stone-soft">
              Sign in
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight">
              Welcome back
            </h1>
            <p className="mt-3 text-stone-soft">
              For case managers, discharge planners, and Ready Rooms staff.
            </p>
          </div>

          <div className="rounded-2xl border border-stone-line bg-cream-50 p-8 shadow-sm">
            <LoginForm next={next} />
          </div>

          <p className="mt-6 text-center text-sm text-stone-soft">
            New here?{" "}
            <Link href="/" className="text-brand-blue-deep hover:underline">
              Learn how Ready Rooms works
            </Link>
          </p>
        </div>
      </main>
    </>
  );
}
