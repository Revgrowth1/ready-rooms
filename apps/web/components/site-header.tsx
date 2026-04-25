import Link from "next/link";
import { createClient, isSupabaseConfigured } from "@/lib/supabase/server";
import { signOut } from "@/app/login/actions";

export async function SiteHeader() {
  let user: { email?: string } | null = null;
  let role: string | null = null;

  if (isSupabaseConfigured()) {
    try {
      const supabase = await createClient();
      const {
        data: { user: u },
      } = await supabase.auth.getUser();
      user = u ?? null;

      if (user) {
        const { data: profile } = await supabase
          .from("profiles")
          .select("role")
          .eq("id", (u as { id: string }).id)
          .maybeSingle();
        role = profile?.role ?? null;
      }
    } catch {
      // Supabase unreachable - render public header
    }
  }

  return (
    <header className="border-b border-stone-line/70 bg-cream/80 backdrop-blur sticky top-0 z-10">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <Link
          href="/"
          className="flex items-center gap-2 font-semibold tracking-tight text-stone-warm"
        >
          <span
            aria-hidden
            className="inline-block h-2.5 w-2.5 rounded-full bg-sage"
          />
          Ready Rooms
        </Link>

        <nav className="flex items-center gap-6 text-sm">
          {user ? (
            <>
              <Link
                href="/refer"
                className="text-stone-soft hover:text-stone-warm"
              >
                Refer
              </Link>
              {role === "admin" && (
                <Link
                  href="/admin"
                  className="text-stone-soft hover:text-stone-warm"
                >
                  Admin
                </Link>
              )}
              <span className="hidden text-stone-soft sm:inline">
                {user.email}
              </span>
              <form action={signOut}>
                <button
                  type="submit"
                  className="text-stone-soft hover:text-stone-warm"
                >
                  Sign out
                </button>
              </form>
            </>
          ) : (
            <Link
              href="/login"
              className="rounded-full bg-sage px-4 py-1.5 text-sm font-medium text-cream hover:bg-sage-deep transition-colors"
            >
              Sign in
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
