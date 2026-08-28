"use client";

import { createClient } from "@supabase/supabase-js";

/**
 * Browser Supabase client.
 *
 * Uses the public anon key only. Row Level Security constrains everything it
 * can reach. The service-role key never exists in this bundle — it is not in
 * .env.local and has no NEXT_PUBLIC_ variable by design.
 *
 * This client is used for authentication (sign up / sign in / session). All
 * application and engineering data flows through the FastAPI backend instead,
 * so there is exactly one place where risk is computed.
 */

const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!url || !anonKey) {
  // Surfaced at import time so a misconfigured deployment fails visibly
  // rather than presenting a login form that silently cannot work.
  console.error(
    "Supabase is not configured. Set NEXT_PUBLIC_SUPABASE_URL and " +
      "NEXT_PUBLIC_SUPABASE_ANON_KEY in frontend/.env.local"
  );
}

export const supabase = createClient(url ?? "", anonKey ?? "", {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
});

export const supabaseConfigured = Boolean(url && anonKey);
