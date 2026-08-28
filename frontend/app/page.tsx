"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { supabase } from "@/lib/supabase";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      router.replace(data.session ? "/citizen/dashboard" : "/login");
    });
  }, [router]);

  return (
    <div className="flex min-h-screen items-center justify-center text-sm text-slate-500">
      Loading SolarGrid AI…
    </div>
  );
}
