"use server";

import { createClient } from "@/lib/supabase/server";
import { revalidatePath } from "next/cache";
import type { IntakeStatus } from "@/lib/types";

const VALID_STATUSES: IntakeStatus[] = [
  "new",
  "reviewing",
  "matched",
  "placed",
  "closed",
];

export async function updateStatus(formData: FormData) {
  const id = String(formData.get("id"));
  const status = String(formData.get("status")) as IntakeStatus;

  if (!id || !VALID_STATUSES.includes(status)) {
    return;
  }

  const supabase = await createClient();
  await supabase.from("intakes").update({ status }).eq("id", id);

  revalidatePath("/admin");
  revalidatePath(`/admin/${id}`);
}
