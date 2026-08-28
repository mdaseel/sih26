"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { supabase, supabaseConfigured } from "@/lib/supabase";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setNotice(null);

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    setBusy(true);

    // The role is never sent from here. A database trigger creates the profile
    // with role = CITIZEN; the column is not client-writable, so a crafted
    // signup cannot request elevated privileges.
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: { full_name: fullName } },
    });
    setBusy(false);

    if (error) {
      setError(error.message);
      return;
    }

    if (data.session) {
      router.replace("/citizen/dashboard");
    } else {
      // The project has email confirmation enabled.
      setNotice(
        "Account created. Check your email to confirm the address, then sign in."
      );
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-6 py-10">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-semibold text-slate-100">
            Create your account
          </h1>
          <p className="mt-2 text-sm text-slate-500">
            Apply for a rooftop solar connection assessment
          </p>
        </div>

        {!supabaseConfigured && (
          <p className="mb-4 rounded-lg border border-red-900 bg-red-950/40 p-3 text-xs text-red-300">
            Supabase is not configured. Set NEXT_PUBLIC_SUPABASE_URL and
            NEXT_PUBLIC_SUPABASE_ANON_KEY in frontend/.env.local.
          </p>
        )}

        <form onSubmit={onSubmit} className="card space-y-4">
          <div>
            <label className="label" htmlFor="name">
              Full name
            </label>
            <input
              id="name"
              required
              className="input"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              autoComplete="name"
            />
          </div>

          <div>
            <label className="label" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              className="input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />
          </div>

          <div>
            <label className="label" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              minLength={8}
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="new-password"
            />
            <p className="mt-1 text-[11px] text-slate-600">At least 8 characters</p>
          </div>

          {error && (
            <p className="rounded-lg border border-red-900 bg-red-950/40 p-2.5 text-xs text-red-300">
              {error}
            </p>
          )}
          {notice && (
            <p className="rounded-lg border border-sky-900 bg-sky-950/40 p-2.5 text-xs text-sky-300">
              {notice}
            </p>
          )}

          <button type="submit" disabled={busy} className="btn-primary w-full">
            {busy ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-slate-500">
          Already registered?{" "}
          <Link href="/login" className="text-sky-400 hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
