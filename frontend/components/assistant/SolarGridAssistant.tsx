"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { usePathname } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import type { AssistantContext, AssistantMessage, SolarGridAssistantAction } from "./assistant-types";

const SUGGESTIONS: Record<string, string[]> = {
  citizen: [
    "Why is my application CAUTION?",
    "Can I install 10 kW here?",
    "What happens after approval?",
    "What does 0.032 pu voltage rise mean?",
  ],
  vendor: [
    "What installations are assigned to me?",
    "Why was this installation returned?",
    "What happens after I submit?",
    "Which application is waiting for DISCOM verification?",
  ],
  discom: [
    "Which buses have low hosting capacity?",
    "Which transformer is heavily loaded?",
    "Explain the ML and physics disagreement",
    "Show me the affected line",
  ],
};

function dispatchAction(action: SolarGridAssistantAction) {
  window.dispatchEvent(new CustomEvent("solargrid:assistant-action", { detail: action }));
}

function renderMarkdown(text: string) {
  // Minimal ChatGPT-style bulletin renderer: headings, bold, bullets, code, blockquote
  const lines = text.split("\n");
  const out: React.ReactNode[] = [];
  let inList = false;
  let listItems: React.ReactNode[] = [];
  const flushList = () => {
    if (listItems.length) {
      out.push(<ul key={`ul-${out.length}`} className="my-2 ml-4 list-disc space-y-1">{listItems}</ul>);
      listItems = [];
      inList = false;
    }
  };
  const inline = (s: string) => {
    // **bold** and `code`
    const parts: React.ReactNode[] = [];
    let last = 0;
    const re = /(\*\*.*?\*\*|`[^`]+`)/g;
    let m: RegExpExecArray | null;
    let idx = 0;
    while ((m = re.exec(s)) !== null) {
      if (m.index > last) parts.push(s.slice(last, m.index));
      const token = m[0];
      if (token.startsWith("**")) parts.push(<strong key={idx++} className="font-semibold" style={{ color: "rgb(var(--ink))" }}>{token.slice(2, -2)}</strong>);
      else if (token.startsWith("`")) parts.push(<code key={idx++} className="rounded bg-slate-800 px-1 py-0.5 font-mono text-xs" style={{ background: "rgb(var(--panel-raised))", color: "rgb(var(--ink))" }}>{token.slice(1, -1)}</code>);
      last = m.index + m[0].length;
    }
    if (last < s.length) parts.push(s.slice(last));
    return parts.length ? parts : s;
  };
  lines.forEach((raw, i) => {
    const line = raw.trimEnd();
    if (line.startsWith("### ")) {
      flushList();
      out.push(<div key={i} className="mt-3 text-sm font-bold" style={{ color: "rgb(var(--ink))" }}>{inline(line.slice(4))}</div>);
    } else if (line.startsWith("## ")) {
      flushList();
      out.push(<div key={i} className="mt-3 text-sm font-bold" style={{ color: "rgb(var(--ink))" }}>{inline(line.slice(3))}</div>);
    } else if (line.startsWith("- ") || line.startsWith("• ")) {
      inList = true;
      listItems.push(<li key={i}>{inline(line.slice(2))}</li>);
    } else if (line.startsWith("> ")) {
      flushList();
      out.push(<div key={i} className="my-2 border-l-2 pl-3 text-xs italic" style={{ borderColor: "rgb(var(--line))", color: "rgb(var(--ink-faint))" }}>{inline(line.slice(2))}</div>);
    } else if (line.trim() === "") {
      flushList();
      out.push(<div key={i} className="h-1" />);
    } else if (line.startsWith("```")) {
      // handled as pre, but we treat as break
      flushList();
    } else {
      flushList();
      out.push(<div key={i} className="text-sm leading-relaxed">{inline(line)}</div>);
    }
  });
  flushList();
  return <div className="space-y-0.5">{out}</div>;
}

export function SolarGridAssistant() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [minimized, setMinimized] = useState(false);
  const [messages, setMessages] = useState<AssistantMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [context, setContext] = useState<AssistantContext>({});
  const [toolStatus, setToolStatus] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [twinContext, setTwinContext] = useState<{ pv_bus?: string; application_id?: string; risk?: string } | null>(null);

  // Keep context in sync with page and global twin selection
  useEffect(() => {
    const page = pathname || "unknown";
    setContext((c) => ({ ...c, page }));
  }, [pathname]);

  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail as { pv_bus?: string; application_id?: string; risk?: string };
      if (detail?.pv_bus) {
        setTwinContext(detail);
        setContext((c) => ({ ...c, pv_bus: detail.pv_bus, application_id: detail.application_id || c.application_id }));
      }
    };
    window.addEventListener("solargrid:twin-context", handler as EventListener);
    return () => window.removeEventListener("solargrid:twin-context", handler as EventListener);
  }, []);

  const scrollToBottom = useCallback(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading, scrollToBottom]);

  const role: "citizen" | "discom" | "vendor" = pathname?.includes("/discom")
    ? "discom"
    : pathname?.includes("/vendor")
      ? "vendor"
      : "citizen";

  const suggestions = SUGGESTIONS[role] || SUGGESTIONS.citizen;

  async function sendMessage(text: string) {
    const trimmed = text.trim();
    if (!trimmed || loading) return;
    const userMsg: AssistantMessage = { id: `u-${Date.now()}`, role: "user", content: trimmed, timestamp: new Date().toISOString() };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);
    setToolStatus("Checking SolarGrid data…");

    // Build history for backend (last 10 turns)
    const history = [...messages, userMsg].slice(-20).map((m) => ({ role: m.role, content: m.content }));

    try {
      // Small staged tool status for UX
      setTimeout(() => setToolStatus("Reading grid assessment…"), 600);
      const res = await api.chat({
        message: trimmed,
        context: {
          page: context.page,
          application_id: context.application_id || twinContext?.application_id || null,
          pv_bus: context.pv_bus || twinContext?.pv_bus || null,
          selected_asset_id: context.selected_asset_id || null,
          selected_asset_type: context.selected_asset_type || null,
        },
        history: history.slice(0, -1), // backend will add current user message
      });

      const assistantMsg: AssistantMessage = {
        id: `a-${Date.now()}`,
        role: "assistant",
        content: res.reply,
        actions: res.actions?.map((a) => ({ type: a.type as any, payload: a.payload })) as any,
        timestamp: new Date().toISOString(),
      };
      setMessages((m) => [...m, assistantMsg]);

      // Auto-dispatch first action if it's a focus
      if (res.actions && res.actions.length > 0) {
        // Don't auto-fly on every message; just make actions available as buttons
      }
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : "SolarGrid AI is temporarily unavailable. Your grid data and existing assessment are unaffected.";
      setMessages((m) => [...m, { id: `e-${Date.now()}`, role: "assistant", content: msg, timestamp: new Date().toISOString() }]);
    } finally {
      setLoading(false);
      setToolStatus(null);
    }
  }

  // Context badge
  const contextLabel = twinContext?.pv_bus
    ? `Bus ${twinContext.pv_bus}${twinContext.risk ? ` · ${twinContext.risk}` : ""}`
    : context.pv_bus
      ? `Bus ${context.pv_bus}`
      : null;

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        aria-label="Open SolarGrid AI Assistant"
        className="fixed bottom-5 right-5 z-50 flex h-14 w-14 items-center justify-center rounded-full shadow-2xl transition-all hover:scale-105 active:scale-95"
        style={{ background: "rgb(var(--brand))", color: "rgb(var(--brand-ink))", boxShadow: "0 8px 32px rgb(var(--shadow) / 0.22)" }}
      >
        <span className="text-xl">☀</span>
      </button>
    );
  }

  return (
    <div
      className={`fixed z-50 flex flex-col overflow-hidden border shadow-2xl transition-all ${minimized ? "h-14" : ""}`}
      style={{
        right: 20,
        bottom: 20,
        width: minimized ? 320 : 420,
        maxWidth: "calc(100vw - 24px)",
        height: minimized ? 56 : "78vh",
        maxHeight: minimized ? 56 : "82vh",
        background: "rgb(var(--panel))",
        borderColor: "rgb(var(--line))",
        borderRadius: 20,
        boxShadow: "0 24px 64px rgb(var(--shadow) / 0.18), 0 0 0 1px rgb(var(--line) / 0.5)",
      }}
    >
      {/* Header */}
      <div
        className="flex shrink-0 items-center justify-between border-b px-4 py-3"
        style={{ borderColor: "rgb(var(--line))", background: "rgb(var(--panel-raised))" }}
      >
        <div className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 items-center justify-center rounded-xl text-sm font-black" style={{ background: "rgb(var(--brand))", color: "rgb(var(--brand-ink))" }}>☀</span>
          <div>
            <div className="text-sm font-bold leading-none" style={{ color: "rgb(var(--ink))" }}>SolarGrid AI</div>
            <div className="text-[11px] font-medium" style={{ color: "rgb(var(--ink-faint))" }}>Grid Assistant</div>
          </div>
          <span className="ml-1 flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-semibold" style={{ borderColor: "rgb(34 197 94 / 0.3)", background: "rgb(34 197 94 / 0.12)", color: "rgb(34 197 94)" }}>
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-500" /> Online
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button onClick={() => setMinimized((m) => !m)} aria-label={minimized ? "Expand" : "Minimize"} className="flex h-7 w-7 items-center justify-center rounded-full border text-xs hover:opacity-80" style={{ borderColor: "rgb(var(--line))", color: "rgb(var(--ink-faint))" }}>
            {minimized ? "▢" : "—"}
          </button>
          <button onClick={() => setOpen(false)} aria-label="Close" className="flex h-7 w-7 items-center justify-center rounded-full border text-xs hover:opacity-80" style={{ borderColor: "rgb(var(--line))", color: "rgb(var(--ink-faint))" }}>✕</button>
        </div>
      </div>

      {!minimized && (
        <>
          {/* Context */}
          <div className="shrink-0 border-b px-4 py-2.5" style={{ borderColor: "rgb(var(--line) / 0.6)", background: "rgb(var(--panel))" }}>
            {contextLabel ? (
              <div className="flex flex-wrap items-center gap-2 text-xs">
                <span className="rounded-full border px-2.5 py-1 font-semibold" style={{ borderColor: "rgb(var(--accent) / 0.3)", background: "rgb(var(--accent) / 0.1)", color: "rgb(var(--accent-strong))" }}>{contextLabel}</span>
                {twinContext?.application_id && <span className="text-[11px]" style={{ color: "rgb(var(--ink-faint))" }}>{twinContext.application_id.slice(0, 8)}</span>}
              </div>
            ) : (
              <div className="text-xs" style={{ color: "rgb(var(--ink-faint))" }}>Ask me about SolarGrid AI, your application, or the grid.</div>
            )}
          </div>

          {/* Messages */}
          <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto px-4 py-4" style={{ background: "rgb(var(--surface))" }}>
            {messages.length === 0 && (
              <div className="space-y-3">
                <div className="rounded-2xl border p-4 text-sm" style={{ borderColor: "rgb(var(--line))", background: "rgb(var(--panel))", color: "rgb(var(--ink-muted))" }}>
                  <div className="font-semibold" style={{ color: "rgb(var(--ink))" }}>Hi, I’m your Grid Assistant.</div>
                  <div className="mt-1 text-xs leading-relaxed">I explain your SolarGrid assessment, grid data, and next steps — using only your real SolarGrid data. I never invent electrical values.</div>
                </div>
                <div className="flex flex-wrap gap-2">
                  {suggestions.map((s) => (
                    <button key={s} onClick={() => sendMessage(s)} className="rounded-full border px-3 py-1.5 text-xs font-medium transition hover:scale-[1.02]" style={{ borderColor: "rgb(var(--line))", background: "rgb(var(--panel))", color: "rgb(var(--ink))" }}>
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            )}
            {messages.map((m) => (
              <div key={m.id} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed ${m.role === "user" ? "rounded-br-md" : "rounded-bl-md"}`}
                  style={
                    m.role === "user"
                      ? { background: "rgb(var(--accent))", color: "white" }
                      : { background: "rgb(var(--panel))", border: "1px solid rgb(var(--line))", color: "rgb(var(--ink))" }
                  }
                >
                  <div className="break-words">{renderMarkdown(m.content)}</div>
                  {m.actions && m.actions.length > 0 && (
                    <div className="mt-2.5 flex flex-wrap gap-1.5">
                      {m.actions.map((a, i) => (
                        <button
                          key={i}
                          onClick={() => dispatchAction(a as SolarGridAssistantAction)}
                          className="rounded-full border px-2.5 py-1 text-[11px] font-semibold hover:opacity-90"
                          style={{ borderColor: "rgb(var(--accent) / 0.3)", background: "rgb(var(--accent) / 0.1)", color: "rgb(var(--accent-strong))" }}
                        >
                          {a.type === "FOCUS_BUS" ? `View Bus ${a.payload.busId}` : a.type === "FOCUS_TRANSFORMER" ? "Show Transformer" : a.type === "FOCUS_LINE" ? "Show Line" : a.type === "HIGHLIGHT_PATH" ? "Highlight Path" : a.type}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="rounded-2xl rounded-bl-md border px-3.5 py-2.5 text-sm" style={{ background: "rgb(var(--panel))", borderColor: "rgb(var(--line))", color: "rgb(var(--ink-faint))" }}>
                  <div className="flex items-center gap-2">
                    <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-500" />
                    {toolStatus || "Thinking…"}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Quick actions when context exists */}
          {twinContext?.pv_bus && messages.length > 0 && !loading && (
            <div className="shrink-0 flex gap-1.5 overflow-x-auto border-t px-3 py-2" style={{ borderColor: "rgb(var(--line) / 0.6)", background: "rgb(var(--panel))" }}>
              <button onClick={() => sendMessage(`Why is bus ${twinContext.pv_bus} ${twinContext.risk || ""}?`)} className="shrink-0 rounded-full border px-3 py-1 text-xs" style={{ borderColor: "rgb(var(--line))", background: "rgb(var(--panel-raised))", color: "rgb(var(--ink))" }}>Explain result</button>
              <button onClick={() => sendMessage(`Show bus ${twinContext.pv_bus} on 3D twin.`)} className="shrink-0 rounded-full border px-3 py-1 text-xs" style={{ borderColor: "rgb(var(--line))", background: "rgb(var(--panel-raised))", color: "rgb(var(--ink))" }}>Show on 3D</button>
              <button onClick={() => dispatchAction({ type: "FOCUS_BUS", payload: { busId: twinContext.pv_bus! } })} className="shrink-0 rounded-full border px-3 py-1 text-xs" style={{ borderColor: "rgb(var(--accent) / 0.3)", background: "rgb(var(--accent) / 0.1)", color: "rgb(var(--accent-strong))" }}>Focus bus</button>
            </div>
          )}

          {/* Composer */}
          <div className="shrink-0 border-t p-3" style={{ borderColor: "rgb(var(--line))", background: "rgb(var(--panel))" }}>
            <div className="flex items-end gap-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage(input);
                  }
                }}
                placeholder="Ask SolarGrid AI…"
                rows={1}
                className="max-h-24 min-h-[44px] flex-1 resize-none rounded-xl border px-3.5 py-2.5 text-sm outline-none focus:border-[rgb(var(--accent))]"
                style={{ background: "rgb(var(--surface-elevated))", borderColor: "rgb(var(--line))", color: "rgb(var(--ink))" }}
              />
              <button onClick={() => sendMessage(input)} disabled={loading || !input.trim()} className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl text-sm font-bold disabled:opacity-50" style={{ background: "rgb(var(--brand))", color: "rgb(var(--brand-ink))" }}>➤</button>
            </div>
            <div className="mt-1.5 text-[10px]" style={{ color: "rgb(var(--ink-ghost))" }}>SolarGrid AI uses only your SolarGrid data. It does not invent electrical values.</div>
          </div>
        </>
      )}
    </div>
  );
}
