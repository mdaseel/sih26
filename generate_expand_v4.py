"""V4 expansion — thin buses to min 18 rows, SAME valid method as Phase2.

Method parity with dataset_generation_phase2.py (read-only, no ML touch):
- net = feeder_network.json (never _ldc), taps FIXED (as shipped)
- sgen p_mw=kw/1000, q_mvar=0, nr, 500 iter, numba=False, tol 1e-3
- BASE = exist only, PV = exist+new, delta = PV-BASE
- thresholds from scenario_config.json, hard `>` then caution `>=`
  (rise hard 0.05/caution 0.03, line 100/80, trafo 100/95, volt 1.05/1.03)
- dedup key (pv_bus, existing, new) against pv_dataset_enriched_augmented.csv
- enrich identical to enrich_augmented.py (incl. total/1.0 when load==0)
- versioned outputs only: pv_dataset_expand_v4.csv (new rows) +
  pv_dataset_enriched_v4_full.csv (1692 + new). Never overwrites v2 model inputs.

Target: every pv_bus >=18 rows (deficit ~34 rows).
"""
import json, copy, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandapower as pp
import pandas as pd
from pathlib import Path

REPO = Path(__file__).resolve().parent
NET_PATH = REPO / "feeder_network.json"
CFG_PATH = REPO / "scenario_config.json"
BASE_CSV = REPO / "pv_dataset_enriched_augmented.csv"
ELEC_CSV = REPO / "electrical_features.csv"
VALID_CSV = REPO / "valid_pv_buses.csv"
OUT_NEW = REPO / "pv_dataset_expand_v4.csv"
OUT_FULL = REPO / "pv_dataset_enriched_v4_full.csv"

cfg = json.loads(CFG_PATH.read_text())
th = cfg["thresholds"]
V_HIGH_HARD = th["voltage_hard_high_pu"]["value"]; V_LOW_HARD = th["voltage_hard_low_pu"]["value"]
V_HIGH_C = th["voltage_caution_high_pu"]["value"]; V_LOW_C = th["voltage_caution_low_pu"]["value"]
V_RISE_HARD = th["voltage_rise_hard_pu"]["value"]; V_RISE_C = th["voltage_rise_caution_pu"]["value"]
LINE_HARD = th["line_loading_hard_pct"]["value"]; LINE_C = th["line_loading_caution_pct"]["value"]
TRAFO_HARD = th["transformer_loading_hard_pct"]["value"]; TRAFO_C = th["transformer_caution_pct"]["value"] if "transformer_caution_pct" in th else th["transformer_loading_caution_pct"]["value"]

def bus_idx(net, name):
    hits = net.bus.index[net.bus.name == str(name)].tolist()
    return hits[0] if hits else None

def extract(net):
    vm = net.res_bus.vm_pu
    return {"min_vm": float(vm.min()), "max_vm": float(vm.max()),
            "min_bus": str(net.bus.name.iloc[vm.idxmin()]), "max_bus": str(net.bus.name.iloc[vm.idxmax()]),
            "ext_p": float(net.res_ext_grid.p_mw.iloc[0]), "ext_q": float(net.res_ext_grid.q_mvar.iloc[0]),
            "losses_p": float(float(net.res_ext_grid.p_mw.iloc[0]) + float(net.sgen.p_mw.sum() if len(net.sgen) else 0) - float(net.load.p_mw.sum() if len(net.load) else 0)),
            "total_load_p": float(net.load.p_mw.sum() if len(net.load) else 0),
            "total_sgen_p": float(net.sgen.p_mw.sum() if len(net.sgen) else 0),
            "max_line": float(net.res_line.loading_percent.max()), "worst_line": str(net.line.name.iloc[net.res_line.loading_percent.idxmax()]),
            "max_trafo": float(net.res_trafo.loading_percent.max()), "worst_trafo": str(net.trafo.name.iloc[net.res_trafo.loading_percent.idxmax()]),
            "line_p": net.res_line.p_from_mw.to_dict(),
            "trafo_p": net.res_trafo.p_hv_mw.to_dict() if 'p_hv_mw' in net.res_trafo.columns else {}}

def run_case(template, bus_id, pv_kw):
    net = copy.deepcopy(template)
    idx = bus_idx(net, bus_id)
    if idx is None: return None, "bus not found"
    if pv_kw > 0:
        pp.create_sgen(net, bus=idx, p_mw=pv_kw/1000.0, q_mvar=0, name=f"PV_{bus_id}_{pv_kw}kW", type="PV")
    try:
        pp.runpp(net, algorithm='nr', max_iteration=500, numba=False, tolerance_mva=1e-3, enforce_q_limits=False)
        if net.converged:
            m = extract(net); m["pv_bus_vm"] = float(net.res_bus.vm_pu.iloc[idx]); m["pp_idx"] = idx
            return m, None
        return None, "not converged"
    except Exception as e:
        return None, str(e)

base = pd.read_csv(BASE_CSV, dtype={'pv_bus': str})
vc = base['pv_bus'].value_counts()
deficit = {b: 18 - int(c) for b, c in vc.items() if c < 18}
print(f"thin buses: {len(deficit)}, deficit rows: {sum(deficit.values())}")
seen = set(zip(base['pv_bus'].astype(str), base['existing_pv_kw'].astype(int), base['new_pv_kw'].astype(int)))
# also track full enriched keys incl existing col name variants
template = pp.from_json(str(NET_PATH))
elec = pd.read_csv(ELEC_CSV, dtype={'bus_id': str}).set_index('bus_id')
valid = pd.read_csv(VALID_CSV, dtype={'bus_id': str}).set_index('bus_id')
map_trafo = valid['transformer_association'].to_dict(); map_section = valid['feeder_section'].to_dict()

CAND_NEW = [8, 12, 18, 22, 35, 45, 60, 80, 110, 130]
CAND_EXIST = [0, 5]
new_rows = []
mid = 1692
base_cache: dict = {}
for bus, need in sorted(deficit.items(), key=lambda x: -x[1]):
    made = 0
    for new_kw in CAND_NEW:
        if made >= need: break
        for exist in CAND_EXIST:
            if made >= need: break
            if (str(bus), int(exist), int(new_kw)) in seen: continue
            key = (str(bus), int(exist))
            if key not in base_cache:
                bm, err = run_case(template, str(bus), int(exist))
                if bm is None:
                    print(f"  SKIP base {bus} exist {exist}: {err}"); continue
                base_cache[key] = bm
            base_m = base_cache[key]
            pv_m, err2 = run_case(template, str(bus), int(exist) + int(new_kw))
            if pv_m is None:
                print(f"  SKIP pv {bus} total {int(exist)+int(new_kw)}: {err2}"); continue
            dvm = pv_m["pv_bus_vm"] - base_m["pv_bus_vm"]
            max_rise = pv_m["max_vm"] - base_m["max_vm"]
            rev = 0; rev_reason = "none"
            if pv_m["ext_p"] < 0: rev = 1; rev_reason = f"source export {pv_m['ext_p']:.3f}MW"
            if rev == 0:
                for lid, pb in base_m["line_p"].items():
                    ppv = pv_m["line_p"].get(lid, 0)
                    if pb > 0.01 and ppv < -0.01: rev = 1; rev_reason = f"line {lid} reversed"; break
            if rev == 0:
                for tid, pb in base_m["trafo_p"].items():
                    ppv = pv_m["trafo_p"].get(tid, 0)
                    if pb > 0.01 and ppv < -0.01: rev = 1; rev_reason = f"trafo {tid} reversed"; break
            ctype, creason = "none", "No violation"
            if pv_m["max_vm"] > V_HIGH_HARD: ctype, creason = "voltage", f"Max voltage {pv_m['max_vm']:.4f} pu at bus {pv_m['max_bus']} exceeds {V_HIGH_HARD}"
            elif pv_m["min_vm"] < V_LOW_HARD: ctype, creason = "voltage", f"Min voltage {pv_m['min_vm']:.4f} pu at bus {pv_m['min_bus']} below {V_LOW_HARD}"
            elif abs(dvm) > V_RISE_HARD: ctype, creason = "voltage_rise", f"Voltage rise at PV bus {bus} {dvm:.4f} pu exceeds {V_RISE_HARD}"
            elif pv_m["max_line"] > LINE_HARD: ctype, creason = "line_loading", f"Line {pv_m['worst_line']} loading {pv_m['max_line']:.1f}% exceeds {LINE_HARD}%"
            elif pv_m["max_trafo"] > TRAFO_HARD: ctype, creason = "transformer_loading", f"Transformer {pv_m['worst_trafo']} loading {pv_m['max_trafo']:.1f}% exceeds {TRAFO_HARD}%"
            label = "SAFE"
            if ctype != "none": label = "CONSTRAINED"
            else:
                cr = []
                if pv_m["max_vm"] > V_HIGH_C: cr.append(f"max {pv_m['max_vm']:.4f}>{V_HIGH_C}")
                if pv_m["min_vm"] < V_LOW_C: cr.append(f"min {pv_m['min_vm']:.4f}<{V_LOW_C}")
                if abs(dvm) >= V_RISE_C: cr.append(f"rise {dvm:.4f}>={V_RISE_C}")
                if pv_m["max_line"] >= LINE_C: cr.append(f"line {pv_m['max_line']:.1f}>={LINE_C}%")
                if pv_m["max_trafo"] >= TRAFO_C: cr.append(f"trafo {pv_m['max_trafo']:.1f}>={TRAFO_C}%")
                if rev == 1: cr.append("reverse flow")
                if cr: label, ctype, creason = "CAUTION", "caution", "; ".join(cr)
            vn = float(template.bus.vn_kv.iloc[pv_m["pp_idx"]])
            load_at = float(template.load[template.load.bus == pv_m["pp_idx"]].p_mw.sum()) if pv_m["pp_idx"] in template.load.bus.values else 0
            mid += 1
            total = int(exist) + int(new_kw)
            row = {"scenario_id": f"S{mid:05d}", "feeder_id": "IEEE_CompTestFeeder", "pv_bus": str(bus),
                   "existing_pv_kw": int(exist), "new_pv_kw": int(new_kw), "total_pv_kw": total,
                   "base_pv_bus_voltage_pu": round(base_m["pv_bus_vm"], 5), "pv_pv_bus_voltage_pu": round(pv_m["pv_bus_vm"], 5),
                   "delta_pv_bus_voltage_pu": round(dvm, 5),
                   "base_min_voltage_pu": round(base_m["min_vm"], 5), "base_max_voltage_pu": round(base_m["max_vm"], 5),
                   "pv_min_voltage_pu": round(pv_m["min_vm"], 5), "pv_max_voltage_pu": round(pv_m["max_vm"], 5),
                   "max_voltage_rise_pu": round(max_rise, 5), "worst_voltage_bus": pv_m["max_bus"],
                   "base_max_line_loading_pct": round(base_m["max_line"], 2), "pv_max_line_loading_pct": round(pv_m["max_line"], 2),
                   "base_max_transformer_loading_pct": round(base_m["max_trafo"], 2), "pv_max_transformer_loading_pct": round(pv_m["max_trafo"], 2),
                   "worst_line": pv_m["worst_line"], "worst_transformer": pv_m["worst_trafo"],
                   "reverse_power_flow": rev, "reverse_reason": rev_reason,
                   "existing_load_at_bus_kw": round(load_at * 1000, 2), "pv_bus_vn_kv": vn,
                   "constraint_type": ctype, "constraint_reason": creason, "label": label, "converged": True,
                   "method": "V4-expansion-same-as-Phase2"}
            # enrich (same as enrich_augmented.py)
            e = elec.loc[str(bus)] if str(bus) in elec.index else None
            sn = float(e["transformer_sn_kva"]) if e is not None else 5000.0
            bv = float(e["base_voltage_pu"]) if e is not None else 0.97
            row["transformer_sn_kva"] = sn; row["base_voltage_pu"] = bv
            row["feeder_distance_km"] = float(e["feeder_distance_km"]) if e is not None else 0
            row["upstream_r_ohm"] = float(e["upstream_r_ohm"]) if e is not None else 0
            row["upstream_x_ohm"] = float(e["upstream_x_ohm"]) if e is not None else 0
            row["upstream_z_ohm"] = float(e["upstream_z_ohm"]) if e is not None else 0
            row["pv_to_transformer_ratio"] = total / sn; row["new_pv_to_transformer_ratio"] = int(new_kw) / sn
            row["load_to_transformer_ratio"] = row["existing_load_at_bus_kw"] / sn if sn else row["existing_load_at_bus_kw"]
            row["pv_penetration_ratio"] = total / row["existing_load_at_bus_kw"] if row["existing_load_at_bus_kw"] != 0 else total / 1.0
            row["transformer_association"] = map_trafo.get(str(bus)); row["feeder_section"] = map_section.get(str(bus))
            row["bus_id"] = str(bus)
            new_rows.append(row); seen.add((str(bus), int(exist), int(new_kw))); made += 1
    print(f"bus {bus}: +{made}/{need}")

if not new_rows:
    print("No rows generated — already >=18/bus."); sys.exit(0)
ndf = pd.DataFrame(new_rows)
ndf.to_csv(OUT_NEW, index=False)
full = pd.concat([base, ndf], ignore_index=True, sort=False)
full.to_csv(OUT_FULL, index=False)
print(f"Saved {len(ndf)} new rows -> {OUT_NEW.name}; full {len(full)} rows -> {OUT_FULL.name}")
print(ndf['label'].value_counts().to_dict())
vc2 = full['pv_bus'].value_counts()
print(f"full per-bus min {vc2.min()} max {vc2.max()} mean {vc2.mean():.1f}")
