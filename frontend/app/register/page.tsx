"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { supabase, supabaseConfigured } from "@/lib/supabase";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState(""); const [email, setEmail] = useState(""); const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null); const [notice, setNotice] = useState<string | null>(null); const [busy, setBusy] = useState(false);
  async function onSubmit(e: React.FormEvent) {
    e.preventDefault(); setError(null); setNotice(null);
    if (password.length < 8) { setError("Password must be at least 8 characters."); return; }
    setBusy(true);
    const { data, error } = await supabase.auth.signUp({ email, password, options: { data: { full_name: fullName } } });
    setBusy(false);
    if (error) { setError(error.message); return; }
    if (data.session) router.replace("/citizen/dashboard"); else setNotice("Account created. Check your email to confirm the address, then sign in.");
  }
  return (
    <div className="flex min-h-screen items-center justify-center px-6 py-10" style={{ background: "radial-gradient(800px 400px at 50% -10%, rgb(var(--accent) / 0.12), transparent), radial-gradient(600px 400px at 90% 90%, rgb(var(--brand) / 0.12), transparent), rgb(var(--surface))" }}>
      <div className="w-full max-w-sm animate-scale-in">
        <div className="mb-8 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl text-lg font-black" style={{ background: "rgb(var(--brand))", color: "rgb(var(--brand-ink))" }}>◈</div>
          <h1 className="mt-4 text-2xl font-bold tracking-tight" style={{ color: "rgb(var(--ink))" }}>Create your account</h1>
          <p className="mt-2 text-sm" style={{ color: "rgb(var(--ink-faint))" }}>Apply for a rooftop solar connection assessment</p>
        </div>
        {!supabaseConfigured && <p className="mb-4 rounded-xl border p-3 text-xs" style={{ borderColor: "rgb(220 38 38 / 0.3)", background: "rgb(254 226 226)", color: "rgb(153 27 27)" }}>Supabase not configured.</p>}
        <form onSubmit={onSubmit} className="card space-y-4 !p-6" style={{ boxShadow: "0 16px 40px rgb(var(--shadow) / 0.1)" }}>
          <div><label className="label" htmlFor="name">Full name</label><input id="name" required className="input" value={fullName} onChange={(e) => setFullName(e.target.value)} autoComplete="name" placeholder="Asha Kumar" /></div>
          <div><label className="label" htmlFor="email">Email</label><input id="email" type="email" required className="input" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" placeholder="asha@example.com" /></div>
          <div><label className="label" htmlFor="password">Password</label><input id="password" type="password" required minLength={8} className="input" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="new-password" placeholder="At least 8 characters" /><p className="mt-1 text-xs" style={{ color: "rgb(var(--ink-faint))" }}>At least 8 characters</p></div>
          {error && <p className="rounded-xl border p-3 text-xs" style={{ borderColor: "rgb(220 38 38 / 0.3)", background: "rgb(254 226 226)", color: "rgb(153 27 27)" }}>{error}</p>}
          {notice && <p className="rounded-xl border p-3 text-xs" style={{ borderColor: "rgb(var(--accent) / 0.3)", background: "rgb(var(--accent) / 0.08)", color: "rgb(var(--accent-strong))" }}>{notice}</p>}
          <button type="submit" disabled={busy} className="btn-primary w-full !py-3">{busy ? "Creating account…" : "Create account →"}</button>
          <p className="text-center text-sm" style={{ color: "rgb(var(--ink-faint))" }}>Already registered? <Link href="/login" className="font-semibold hover:underline" style={{ color: "rgb(var(--accent-strong))" }}>Sign in</Link></p>
        </form>
      </div>
    </div>
  );
}
