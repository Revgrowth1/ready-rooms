import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { SiteHeader } from "@/components/site-header";

export default async function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) redirect("/login?next=/admin");

  const { data: profile } = await supabase
    .from("profiles")
    .select("role")
    .eq("id", user.id)
    .maybeSingle();

  if (profile?.role !== "admin") {
    return (
      <>
        <SiteHeader />
        <main className="flex flex-1 items-center justify-center px-6 py-16">
          <div className="max-w-md text-center">
            <p className="text-xs uppercase tracking-[0.2em] text-stone-soft">
              Admin only
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight">
              You don&apos;t have admin access yet.
            </h1>
            <p className="mt-3 text-stone-soft">
              Ask your Ready Rooms admin to upgrade your role. Until then, you
              can submit and track your own referrals.
            </p>
          </div>
        </main>
      </>
    );
  }

  return (
    <>
      <SiteHeader />
      {children}
    </>
  );
}
