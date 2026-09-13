"""POST /api/chat — SolarGrid AI Grid Assistant.

Non-streaming first, streaming optional later. Backend-only NVIDIA key.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser, get_current_user
from app.core.config import get_settings
from app.services.ai_assistant import (
    SYSTEM_PROMPT,
    _trim_history,
    build_tool_messages,
    call_nvidia,
    execute_tool,
    extract_reply,
    rule_based_fallback,
    tool_specs,
)

log = logging.getLogger("solargrid.assistant")
router = APIRouter(prefix="/api", tags=["assistant"])


class ChatContext(BaseModel):
    page: str | None = None
    application_id: str | None = None
    pv_bus: str | None = None
    selected_asset_id: str | None = None
    selected_asset_type: str | None = None
    assessment_id: str | None = None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    context: ChatContext | None = None
    history: list[dict[str, Any]] = Field(default_factory=list)
    stream: bool = False  # future; currently non-streaming


class ChatAction(BaseModel):
    type: str
    payload: dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    reply: str
    actions: list[ChatAction] = Field(default_factory=list)
    context_used: dict[str, Any] | None = None
    disclaimer: str | None = None


def _heuristic_actions(text: str, context: ChatContext | None, tool_results: list[dict[str, Any]]) -> list[ChatAction]:
    """Derive safe Cesium/2D focus actions from tool results + context."""
    actions: list[ChatAction] = []
    low = text.lower()

    # If tool returned a bus/transformer/line, offer focus
    for res in tool_results:
        if "bus" in res and isinstance(res["bus"], dict):
            bid = res["bus"].get("bus_id") or res["bus"].get("busId")
            if bid:
                actions.append(ChatAction(type="FOCUS_BUS", payload={"busId": str(bid)}))
        if "transformer" in res and isinstance(res["transformer"], dict):
            t = res["transformer"].get("asset_code") or res["transformer"].get("name")
            if t:
                actions.append(ChatAction(type="FOCUS_TRANSFORMER", payload={"transformerId": str(t)}))
        if "metrics" in res and isinstance(res["metrics"], dict):
            pv = res["metrics"].get("pv_bus")
            if pv:
                actions.append(ChatAction(type="FOCUS_BUS", payload={"busId": str(pv)}))
        if "elements" in res and isinstance(res["elements"], dict):
            path = res["elements"].get("path") or []
            if path:
                actions.append(ChatAction(type="HIGHLIGHT_PATH", payload={"assetIds": path}))

    # Heuristic from context
    if context and context.pv_bus:
        if any(k in low for k in ["show", "focus", "highlight", "3d", "twin", "path"]):
            actions.append(ChatAction(type="FOCUS_BUS", payload={"busId": str(context.pv_bus)}))
            if "transformer" in low:
                actions.append(ChatAction(type="FOCUS_TRANSFORMER", payload={"transformerId": "auto"}))
            if "line" in low:
                actions.append(ChatAction(type="FOCUS_LINE", payload={"lineId": "auto"}))

    # Deduplicate by type+payload
    seen = set()
    uniq: list[ChatAction] = []
    for a in actions:
        key = (a.type, tuple(sorted(a.payload.items())))
        if key not in seen:
            seen.add(key)
            uniq.append(a)
    return uniq[:4]


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest, user: CurrentUser = Depends(get_current_user)
) -> ChatResponse:
    settings = get_settings()
    if not settings.nvidia_configured:
        raise HTTPException(
            status_code=503,
            detail="SolarGrid AI assistant is temporarily unavailable (LLM not configured). Your grid data and assessments are unaffected.",
        )

    # Fast path: common intents answered without NIM (never times out, instant)
    q_low = payload.message.lower()
    import re as _re2

    # Count — ChatGPT-style bulletin
    if any(k in q_low for k in ["how many application", "how many applications", "how many did i apply"]):
        res = await execute_tool("list_my_applications", {}, user)
        if "count" in res:
            reply = f"### Your SolarGrid Applications — {res['count']} total\n\n"
            if res.get("applications"):
                for a in res["applications"][:10]:
                    status_badge = {"APPROVED":"✅ APPROVED","VERIFIED":"✅ VERIFIED","VENDOR_SELECTED":"🔧 VENDOR SELECTED","INSTALLING":"🔧 INSTALLING","REJECTED":"❌ REJECTED"}.get(a.get("status"), a.get("status"))
                    reply += f"- **{a['application_number']}** — {status_badge} · Bus **{a.get('pv_bus','—')}** · **{a.get('new_pv_kw','—')} kW**\n"
                reply += f"\n> Ask `Tell me about SG-XXXX` for details on any one, or `Show Bus 734 on 3D twin` to fly there."
            else:
                reply += "_No applications yet — create one via **Citizen → New application**._"
            return ChatResponse(reply=reply, actions=[], context_used=payload.context.model_dump() if payload.context else None)

    # Show bus on 3D twin — direct action, no LLM
    m_bus_show = _re2.search(r"bus\s*(\d+)", q_low)
    if m_bus_show and any(k in q_low for k in ["show", "focus", "highlight", "display", "3d twin", "twin", "map"]):
        bid = m_bus_show.group(1)
        return ChatResponse(
            reply=f"Showing **Bus {bid}** on the 3D twin — flying the camera there and highlighting its path. If you don’t see it, make sure the twin is visible (toggle **3D grid twin**).",
            actions=[ChatAction(type="FOCUS_BUS", payload={"busId": bid})],
            context_used=payload.context.model_dump() if payload.context else None,
        )

    # Specific application by number (SG-XXXX) — direct lookup, with intent-aware details
    m_sg = _re2.search(r"sg-[a-f0-9]{6,}", q_low)
    if m_sg:
        sg = m_sg.group(0).upper()
        res = await execute_tool("list_my_applications", {}, user)
        hit = next((a for a in res.get("applications", []) if a.get("application_number", "").upper() == sg), None)
        if hit:
            det = await execute_tool("get_application_details", {"application_id": hit["id"]}, user)
            ass = await execute_tool("get_assessment", {"application_id": hit["id"]}, user)
            app = det.get("application", hit)
            # Intent: physics simulation values?
            asks_physics = any(k in q_low for k in ["physics simulation values", "simulation values", "physics values", "what is the physics simulation"])
            if asks_physics and "assessment" in ass and isinstance(ass["assessment"], dict):
                a = ass["assessment"]
                m = a.get("metrics", {}) if isinstance(a.get("metrics"), dict) else {}
                eng = a.get("engineering", {}) if isinstance(a.get("engineering"), dict) else {}
                ml = a.get("ml", {}) if isinstance(a.get("ml"), dict) else {}
                reply = f"### {app.get('application_number')} — Physics Simulation Values (Power-Flow)\n\n"
                reply += f"- **Bus:** {app.get('pv_bus')} · **Solar:** {app.get('existing_pv_kw')} kW existing + **{app.get('new_pv_kw')} kW new** (total {app.get('total_pv_kw')} kW) · **Status:** `{app.get('status')}`\n"
                reply += f"- **Voltages:** PV bus **{m.get('pv_voltage_pu','—')} pu** (base {m.get('base_voltage_pu','—')} pu, **rise {m.get('voltage_rise_pu','—')} pu**), feeder **{m.get('feeder_min_voltage_pu','—')} – {m.get('feeder_max_voltage_pu','—')} pu** (min at {m.get('min_voltage_bus','—')}, max at {m.get('max_voltage_bus','—')})\n"
                reply += f"- **Loadings:** Transformer **{m.get('worst_transformer','—')} {m.get('max_transformer_loading_pct','—')}%** (base {m.get('base_max_transformer_loading_pct','—')}%), Line **{m.get('worst_line','—')} {m.get('max_line_loading_pct','—')}%** (base {m.get('base_max_line_loading_pct','—')}%)\n"
                reply += f"- **Losses & Flow:** Power loss **{m.get('power_loss_kw','—')} kW** (Δ {m.get('delta_losses_kw','—')} kW), Grid supply **{m.get('base_total_p_kw','—')} → {m.get('pv_total_p_kw','—')} kW**, Reverse: **{m.get('reverse_power_flow','—')}** ({m.get('reverse_reason','')})\n"
                reply += f"- **Engineering:** **{eng.get('engineering_risk','—')}** — {eng.get('constraint_type','—')}: {eng.get('constraint_reason','')}\n"
                reply += f"- **ML pre-screen:** **{ml.get('prediction','—')}** (safe {ml.get('safe_probability',0):.2f} / caution {ml.get('caution_probability',0):.2f} / constrained {ml.get('constrained_probability',0):.2f})\n"
                reply += f"> **Power-flow decides** — thresholds from `scenario_config.json` (hard `>` vs caution `>=`).\n"
                return ChatResponse(reply=reply, actions=[ChatAction(type="FOCUS_BUS", payload={"busId": str(app.get('pv_bus'))})], context_used=payload.context.model_dump() if payload.context else None)
            # Intent: does user ask for model inputs?
            asks_inputs = any(k in q_low for k in ["input given to the model", "what are the input", "inputs to the model", "features given", "what inputs"])
            if asks_inputs and "assessment" in ass and isinstance(ass["assessment"], dict):
                ml = ass["assessment"].get("ml", {})
                feats = ml.get("features_used", {}) if isinstance(ml.get("features_used"), dict) else {}
                reply = f"### {app.get('application_number')} — Model Inputs (18 features)\n\n"
                reply += f"Bus **{app.get('pv_bus')}** · Requested **{app.get('new_pv_kw')} kW** (existing {app.get('existing_pv_kw')} kW)\n\n"
                reply += "**Pre-screen inputs (what the Random Forest saw):**\n"
                if feats:
                    for k, v in feats.items():
                        reply += f"- `{k}`: **{v}**\n"
                    reply += f"\n> No voltages/loadings — those are power-flow outputs, not inputs (no leakage). Tree count: **{ml.get('tree_count','—')}**, model `{ml.get('model_file','suryagrid_model_v2.pkl')}`.\n"
                else:
                    reply += "_No stored feature vector — this assessment may pre-date input logging._\n"
                eng = ass["assessment"].get("engineering", {}) if isinstance(ass["assessment"].get("engineering"), dict) else {}
                reply += f"\n**Result:** ML **{ml.get('prediction','—')}** (safe {ml.get('safe_probability','—'):.2f}) → Engineering **{eng.get('engineering_risk','—')}** — physics wins.\n"
                return ChatResponse(reply=reply, actions=[ChatAction(type="FOCUS_BUS", payload={"busId": str(app.get('pv_bus'))})], context_used=payload.context.model_dump() if payload.context else None)

            # Default: full application bulletin
            # Try to get richer fields via direct DB for this app (address, applicant, created_at)
            full_app = None
            try:
                from app.db.service import db as _db

                full_app = _db.get_application(user.access_token, hit["id"])
            except Exception:
                full_app = app
            fa = full_app or app
            reply = f"### {fa.get('application_number')} — **{fa.get('status')}**\n\n"
            reply += f"- **Applicant:** {fa.get('applicant_name','—')} · **Phone:** {fa.get('contact_phone','—')}\n"
            reply += f"- **Address:** {fa.get('address_line','—')}, {fa.get('district','—')}, {fa.get('state','—')} {fa.get('pincode','')}\n"
            reply += f"- **Site:** {fa.get('latitude','—')}, {fa.get('longitude','—')} · **Bus:** **{fa.get('pv_bus')}** ({fa.get('feeder_section','—')} via {fa.get('transformer_association','—')})\n"
            reply += f"- **Solar:** Existing **{fa.get('existing_pv_kw')} kW** → Requested **{fa.get('new_pv_kw')} kW** (total **{fa.get('total_pv_kw')} kW**) · Roof {fa.get('roof_area_sqm','—')} m², {fa.get('roof_type','—')}\n"
            reply += f"- **Status:** `{fa.get('status')}` · Created {str(fa.get('created_at',''))[:10]}\n"
            if "assessment" in ass and isinstance(ass["assessment"], dict):
                eng = ass["assessment"].get("engineering", {})
                ml = ass["assessment"].get("ml", {})
                metrics = ass["assessment"].get("metrics", {})
                reply += f"\n**Assessment:**\n"
                reply += f"- **Engineering:** **{eng.get('engineering_risk','—')}** — {eng.get('constraint_type','—')}: {eng.get('constraint_reason','')}\n"
                reply += f"- **ML pre-screen:** **{ml.get('prediction','—')}** (safe {ml.get('safe_probability',0):.2f}, caution {ml.get('caution_probability',0):.2f}, constrained {ml.get('constrained_probability',0):.2f})\n"
                if metrics:
                    reply += f"- **Power-flow:** PV bus {metrics.get('pv_voltage_pu','—')} pu (rise {metrics.get('voltage_rise_pu','—')} pu), Trafo {metrics.get('max_transformer_loading_pct','—')}%, Line {metrics.get('max_line_loading_pct','—')}%, Reverse: {metrics.get('reverse_power_flow','—')}\n"
                reply += f"> **Power-flow decides** — if ML says SAFE but physics says CONSTRAINED, physics wins. Thresholds from `scenario_config.json`.\n"
            else:
                reply += f"\n_No stored assessment yet — run one via **DISCOM → Applications → Assess**._\n"
            return ChatResponse(reply=reply, actions=[ChatAction(type="FOCUS_BUS", payload={"busId": str(fa.get('pv_bus'))})], context_used=payload.context.model_dump() if payload.context else None)

    # Subsidy — PM Surya Ghar
    if "subsidy" in q_low:
        m_kw_sub = _re2.search(r"(\d+(?:\.\d+)?)\s*kW", q_low)
        if m_kw_sub:
            try:
                res = await execute_tool("get_subsidy_estimate", {"capacity_kw": float(m_kw_sub.group(1))}, user)
                if "subsidy" in res:
                    s = res["subsidy"]
                    reply = f"### Subsidy for {m_kw_sub.group(1)} kW (PM Surya Ghar)\n\n"
                    reply += f"- **Eligible capacity:** {s.get('eligible_capacity_kw')} kW\n"
                    reply += f"- **Subsidy amount:** **{s.get('currency','INR')} {s.get('amount',0):,.0f}**\n"
                    if s.get("breakdown"):
                        reply += "\n**Breakdown:**\n"
                        for b in s["breakdown"]:
                            reply += f"  - {b.get('from_kw')}–{b.get('to_kw')} kW × {b.get('rate_per_kw')} = {b.get('amount')}\n"
                    if s.get("capped"):
                        reply += f"\n* Capped at max {s.get('max_subsidy')} — {s.get('disclaimer','')}*\n"
                    reply += f"\n> {s.get('disclaimer','')} — verify on the official portal."
                    return ChatResponse(reply=reply, actions=[], context_used=payload.context.model_dump() if payload.context else None)
            except Exception:
                pass

    # Vendor queries
    if "vendor" in q_low or "installer" in q_low:
        if any(k in q_low for k in ["how many vendor", "how many installer", "number of vendor"]):
            res = await execute_tool("list_vendors", {}, user)
            if "count" in res:
                reply = f"### Vendors — {res['count']} total\n\n"
                for v in res.get("vendors", [])[:10]:
                    reply += f"- **{v.get('business_name')}** — {v.get('district','—')}, {v.get('state','—')} · Rating **{v.get('rating','—')}/5** · {v.get('status')}\n"
                return ChatResponse(reply=reply, actions=[], context_used=payload.context.model_dump() if payload.context else None)
        if any(k in q_low for k in ["rating", "where are they", "where are vendor", "location"]):
            res = await execute_tool("list_vendors", {}, user)
            if "vendors" in res:
                reply = "### Vendors — Locations & Ratings\n\n"
                for v in res["vendors"][:10]:
                    reply += f"- **{v.get('business_name')}** — **{v.get('rating','—')}/5** · {v.get('district','—')}, {v.get('state','—')} · Areas: {', '.join(v.get('service_areas',[])[:3]) or '—'}\n"
                reply += "\n> Only **APPROVED and active** vendors are shown to citizens."
                return ChatResponse(reply=reply, actions=[], context_used=payload.context.model_dump() if payload.context else None)

    # Finished applications
    if any(k in q_low for k in ["finished fully", "finished", "verified", "completed fully", "how many.*verified"]):
        if "application" in q_low:
            res = await execute_tool("get_finished_applications", {}, user)
            if "finished" in res:
                reply = f"### Finished Applications — {res['finished']} of {res['total']} verified\n\n"
                for a in res.get("finished_applications", [])[:5]:
                    reply += f"- **{a.get('application_number')}** — Bus {a.get('pv_bus')} · {a.get('new_pv_kw')} kW\n"
                if res["finished"] == 0:
                    reply += "_No application is VERIFIED yet — they are in progress._"
                return ChatResponse(reply=reply, actions=[], context_used=payload.context.model_dump() if payload.context else None)

    # Hosting/capable — direct power-flow answer + focus
    if any(k in q_low for k in ["capable", "hosting capacity", "how much can", "maximum pv", "max pv"]) and ("bus" in q_low or (payload.context and payload.context.pv_bus)):
        bus_id = None
        m_b = _re2.search(r"bus\s*(\d+)", q_low)
        if m_b:
            bus_id = m_b.group(1)
        elif payload.context and payload.context.pv_bus:
            bus_id = str(payload.context.pv_bus)
        if bus_id:
            try:
                from app.services.hosting_capacity import get_hosting_capacity_service

                cap = get_hosting_capacity_service().capacity_for(bus_id, 0)
                reply = (
                    f"**Bus {bus_id}** can host about **{cap.hosting_capacity_kw:.1f} kW** before a hard limit. "
                    f"**Limiting:** {cap.limiting_constraint} — {cap.limiting_reason}. "
                    f"At that point risk would be **{cap.risk_at_capacity}** (bisection, {cap.power_flows_run} solves)."
                )
                return ChatResponse(reply=reply, actions=[ChatAction(type="FOCUS_BUS", payload={"busId": bus_id})], context_used=payload.context.model_dump() if payload.context else None)
            except Exception:
                pass

    fast = rule_based_fallback(payload.message, payload.context.model_dump() if payload.context else None)
    if fast:
        # Attach focus action for show-bus even when fast path handled it via text
        m_bus_fast = _re2.search(r"bus\s*(\d+)", q_low)
        acts = []
        if m_bus_fast and any(k in q_low for k in ["show", "focus", "highlight"]):
            acts = [ChatAction(type="FOCUS_BUS", payload={"busId": m_bus_fast.group(1)})]
        # Hosting fast path may need focus too
        if not acts and any(k in q_low for k in ["capable", "hosting capacity"]) and m_bus_fast:
            acts = [ChatAction(type="FOCUS_BUS", payload={"busId": m_bus_fast.group(1)})]
        return ChatResponse(reply=fast, actions=acts, context_used=payload.context.model_dump() if payload.context else None)

    # Build messages
    history = _trim_history(payload.history)
    # Inject context as a hidden user note for grounding (not shown to user)
    context_note = ""
    if payload.context:
        context_note = f"[Context page={payload.context.page} pv_bus={payload.context.pv_bus} app={payload.context.application_id} asset={payload.context.selected_asset_type}:{payload.context.selected_asset_id} user_role={user.role.value}]"
    messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in history:
        if h.get("role") in ("user", "assistant", "tool") and isinstance(h.get("content"), str):
            messages.append({"role": h["role"], "content": h["content"][:6000]})
    user_content = payload.message
    if context_note:
        user_content = f"{context_note}\n\nUser: {payload.message}"
    messages.append({"role": "user", "content": user_content})

    tools = tool_specs()

    # First LLM turn (may request tools) — with graceful fallback for retired models / 410
    try:
        data = await call_nvidia(messages, tools=tools)
    except httpx.HTTPStatusError as e:
        status = e.response.status_code if hasattr(e, "response") and e.response is not None else 502
        body = e.response.text[:600] if hasattr(e, "response") and e.response is not None else str(e)
        log.warning("NIM HTTP %s: %s", status, body)
        # Model retired (410) or not entitled (404) — try fallback to rule-based answer below
        if status in (404, 410, 429):
            data = None  # trigger fallback
        else:
            raise HTTPException(status_code=502, detail="Assistant upstream error. Please try again.") from e
        if data is None:
            # Fallback: answer "Can I install X kW?" directly via hosting capacity when context has pv_bus
            import re

            q = payload.message.lower()
            m_kw = re.search(r"(\d+(?:\.\d+)?)\s*kW", q)
            if m_kw and payload.context and payload.context.pv_bus:
                try:
                    from app.services.hosting_capacity import get_hosting_capacity_service

                    cap = get_hosting_capacity_service().capacity_for(payload.context.pv_bus, 0)
                    requested = float(m_kw.group(1))
                    hosting = cap.hosting_capacity_kw
                    verdict = "within" if requested <= hosting else "exceeds"
                    reply = (
                        f"Based on the current SolarGrid simulation for Bus {payload.context.pv_bus}, "
                        f"the estimated hosting capacity is **{hosting:.1f} kW** (limiting: {cap.limiting_constraint}). "
                        f"Your requested **{requested:.1f} kW {verdict}** this limit. "
                        f"{'You can proceed, but DISCOM will still review the detailed power-flow.' if requested <= hosting else 'Consider reducing capacity or ask for a detailed assessment.'} "
                        f"This is from the deterministic power-flow (bisection), not the pre-screen ML."
                    )
                    actions = [ChatAction(type="FOCUS_BUS", payload={"busId": payload.context.pv_bus})]
                    return ChatResponse(reply=reply, actions=actions, context_used=payload.context.model_dump() if payload.context else None)
                except Exception:
                    pass
            # Return a grounded fallback instead of 502 for timeouts, so UI never shows "Backend timed out"
        import re as _re

        # Try to give a useful rule-based answer even without LLM
        q_low = payload.message.lower()
        if any(k in q_low for k in ["apply", "new application"]):
            fb = "To apply: **Citizen → Dashboard → New application** → fill site (address + lat/lon), *Requested new solar* (Residential 1–10 kW, Commercial/Industrial 1–500 kW), roof & consumption → optionally use **3D Rooftop Placement → Use This Placement** → **Submit**. You’ll be screened instantly (ML + power-flow) and can track **Progress** in My applications. No sanctioned load needed."
            return ChatResponse(reply=fb, actions=[], context_used=payload.context.model_dump() if payload.context else None)
        m_kw = _re.search(r"(\d+(?:\.\d+)?)\s*kW", q_low)
        if m_kw and payload.context and payload.context.pv_bus:
            try:
                from app.services.hosting_capacity import get_hosting_capacity_service

                cap = get_hosting_capacity_service().capacity_for(payload.context.pv_bus, 0)
                requested = float(m_kw.group(1))
                hosting = cap.hosting_capacity_kw
                verdict = "within" if requested <= hosting else "exceeds"
                reply = (
                    f"Based on the current SolarGrid simulation for Bus {payload.context.pv_bus}, "
                    f"hosting capacity is **{hosting:.1f} kW** ({cap.limiting_constraint}). "
                    f"Requested **{requested:.1f} kW {verdict}** it. "
                )
                return ChatResponse(reply=reply, actions=[ChatAction(type="FOCUS_BUS", payload={"busId": payload.context.pv_bus})], context_used=payload.context.model_dump() if payload.context else None)
            except Exception:
                pass
        # Generic graceful fallback — no 502, keep chat usable
        return ChatResponse(
            reply=(
                "I’m having trouble reaching the AI model right now (upstream timeout), but your SolarGrid data is fine.\n\n"
                "Try asking with a bit more context, e.g.:\n"
                "• `Why is my application CAUTION?` (with an application selected)\n"
                "• `Can I install 10 kW at Bus 734?`\n"
                "• `What happens after approval?` \n\n"
                "Or tell me your **Bus ID / Application ID** and I’ll pull the real assessment, hosting capacity, or transformer data directly."
            ),
            actions=[],
            context_used=payload.context.model_dump() if payload.context else None,
        )
    except Exception as e:
        log.exception("NIM call failed")
        if "not configured" in str(e):
            raise HTTPException(status_code=503, detail=str(e)) from e
        # Same graceful fallback for any other NIM failure
        return ChatResponse(
            reply=(
                "SolarGrid AI is temporarily slow to answer (model timeout), but your grid data and assessments are unaffected.\n\n"
                "You can still ask:\n"
                "• `Why is this constrained?` (select an assessment)\n"
                "• `Show Bus 734 on 3D twin`\n"
                "• `Explain voltage rise`\n\n"
                "Try again in a few seconds, or include a **Bus ID** for a direct data lookup."
            ),
            actions=[],
            context_used=payload.context.model_dump() if payload.context else None,
        )

    content, tool_calls = extract_reply(data)

    tool_results: list[dict[str, Any]] = []
    if tool_calls:
        # Execute each tool under the caller's permissions
        for tc in tool_calls:
            fname = tc.get("function", {}).get("name", "")
            raw_args = tc.get("function", {}).get("arguments", "{}")
            # arguments may be stringified JSON
            import json

            try:
                args = json.loads(raw_args) if isinstance(raw_args, str) else (raw_args or {})
            except Exception:
                args = {}
            res = await execute_tool(fname, args, user)
            tool_results.append(res)

        # Second turn: feed tool results back
        messages.append({"role": "assistant", "content": content or "", "tool_calls": tool_calls})  # type: ignore[arg-type]
        messages.extend(build_tool_messages(tool_calls, tool_results))
        try:
            data2 = await call_nvidia(messages, tools=None)
            content2, _ = extract_reply(data2)
            if content2:
                content = content2
        except Exception:
            # If second turn fails, still return tool-grounded partial
            if not content:
                content = ""

    if not content:
        # Grounded fallback from tool results — never hallucinate, but never empty
        if tool_results:
            # Prefer list_my_applications
            for r in tool_results:
                if "count" in r and "applications" in r:
                    content = f"You have **{r['count']}** application(s) in SolarGrid. " + (
                        ", ".join([f"{a['application_number']} ({a['status']}, Bus {a.get('pv_bus','—')}, {a.get('new_pv_kw','—')} kW)" for a in r["applications"][:5]]) if r["applications"] else "No applications found."
                    )
                    break
            if not content:
                for r in tool_results:
                    if "thresholds" in r:
                        th = r["thresholds"]
                        content = (
                            "Based on the current SolarGrid simulation, classification is: **CONSTRAINED** if any hard limit is crossed "
                            f"(maxV>1.05, minV<0.90, |rise|>0.05, line>100% or trafo>100%); else **CAUTION** if "
                            f"(maxV>1.03, |rise|≥0.03, line≥80%, trafo≥95% or reverse flow); else **SAFE**. "
                            f"Your thresholds: {th}. Power-flow decides, ML (Random Forest) is only the pre-screen."
                        )
                        break
            if not content:
                for r in tool_results:
                    if "hosting_capacity" in r and isinstance(r["hosting_capacity"], dict):
                        hc = r["hosting_capacity"]
                        bus = hc.get("bus_id") or payload.context.pv_bus if payload.context else "—"
                        content = (
                            f"**Bus {bus}** can host about **{hc.get('hosting_capacity_kw','—')} kW** before hitting a hard limit. "
                            f"**Limiting:** {hc.get('limiting_constraint','—')} — {hc.get('limiting_reason','')}. "
                            f"Risk at that capacity: **{hc.get('risk_at_capacity','—')}** (bisection, {hc.get('power_flows_run','—')} solves, {hc.get('method','')})."
                        )
                        break
            if not content:
                for r in tool_results:
                    if "assessment" in r and isinstance(r["assessment"], dict):
                        a = r["assessment"]
                        eng = a.get("engineering", {}) if isinstance(a.get("engineering"), dict) else {}
                        ml = a.get("ml", {}) if isinstance(a.get("ml"), dict) else {}
                        content = (
                            f"Assessment for this application: **engineering {eng.get('engineering_risk','—')}** ({eng.get('constraint_type','—')}: {eng.get('constraint_reason','')}) — "
                            f"ML was **{ml.get('prediction','—')}** (safe {ml.get('safe_probability','—')}). "
                            f"Power-flow is the source of truth; if ML disagrees, physics wins."
                        )
                        break
            if not content:
                # Generic tool dump fallback (still grounded)
                try:
                    import json as _json

                    content = "Here is what I found in SolarGrid data:\n```json\n" + _json.dumps(tool_results[0], indent=2)[:1800] + "\n```"
                except Exception:
                    content = "I found data but couldn't format it. Please try asking more specifically."
        if not content:
            content = "I don't have that information from the current SolarGrid data. Please select an application, bus, or assessment and try a more specific question."

    actions = _heuristic_actions(content, payload.context, tool_results)

    disclaimer = None
    if any("prototype" in (r.get("error") or "") or "synthetic" in content.lower() for r in tool_results):
        disclaimer = None
    # Always remind when grid is synthetic (per honesty rules, but not on every turn — only when relevant)
    if payload.context and payload.context.pv_bus:
        # Don't spam disclaimer; let system prompt handle synthetic note
        pass

    return ChatResponse(reply=content, actions=actions, context_used=payload.context.model_dump() if payload.context else None, disclaimer=disclaimer)


@router.get("/chat/health")
async def chat_health() -> dict[str, Any]:
    s = get_settings()
    return {
        "nvidia_configured": s.nvidia_configured,
        "nvidia_base_url": s.nvidia_nim_base_url,
        "nvidia_model": s.nvidia_nim_model,
        "status": "ok" if s.nvidia_configured else "unconfigured",
    }
