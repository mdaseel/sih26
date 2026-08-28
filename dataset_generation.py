"""
SuryaGrid AI Phase 1 - PV Scenario Generation
- BASE/PV method (existing vs new)
- Fixed regulator taps
- Unity PF sgen
- Thresholds from scenario_config.json
- No TXT tuning
"""
import json, copy, csv, math, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandapower as pp
import pandas as pd
import numpy as np

CONFIG_PATH = r"C:\Users\ASUS\Documents\suryaghar\scenario_config.json"
NET_PATH = r"C:\Users\ASUS\Documents\suryaghar\feeder_network.json"
VALID_BUSES_CSV = r"C:\Users\ASUS\Documents\suryaghar\valid_pv_buses.csv"
OUTPUT_CSV = r"C:\Users\ASUS\Documents\suryaghar\pv_dataset_test.csv"

with open(CONFIG_PATH, 'r') as f:
    cfg = json.load(f)

th = cfg["thresholds"]
V_LOW_HARD = th["voltage_hard_low_pu"]["value"]
V_HIGH_HARD = th["voltage_hard_high_pu"]["value"]
V_LOW_CAUTION = th["voltage_caution_low_pu"]["value"]
V_HIGH_CAUTION = th["voltage_caution_high_pu"]["value"]
V_RISE_HARD = th["voltage_rise_hard_pu"]["value"]
V_RISE_CAUTION = th["voltage_rise_caution_pu"]["value"]
LINE_HARD = th["line_loading_hard_pct"]["value"]
LINE_CAUTION = th["line_loading_caution_pct"]["value"]
TRAFO_HARD = th["transformer_loading_hard_pct"]["value"]
TRAFO_CAUTION = th["transformer_loading_caution_pct"]["value"]

# Load base network once to get bus mapping
base_net0 = pp.from_json(NET_PATH)
# Ensure power flow config
def bus_name_to_idx(net, bus_id_str):
    # net.bus.name is string
    hits = net.bus.index[net.bus.name == str(bus_id_str)].tolist()
    if hits:
        return hits[0]
    return None

def extract_metrics(net):
    """Extract required outputs from a solved net."""
    # Voltages
    vm = net.res_bus.vm_pu
    va = net.res_bus.va_degree
    # Map bus name
    # min/max
    min_vm = vm.min()
    max_vm = vm.max()
    min_idx = vm.idxmin()
    max_idx = vm.idxmax()
    min_bus_name = net.bus.name.iloc[min_idx]
    max_bus_name = net.bus.name.iloc[max_idx]
    # totals
    ext_p = float(net.res_ext_grid.p_mw.iloc[0]) if len(net.res_ext_grid)>0 else 0
    ext_q = float(net.res_ext_grid.q_mvar.iloc[0]) if len(net.res_ext_grid)>0 else 0
    # losses: sum of all bus p + ext? simpler: ext_p - sum(load p) + sgen p
    # But net.res_bus.p_mw is net injection per bus (negative for load). Use ext + sgen - load? Use pandapower losses via res_line?
    # Approximate losses as ext_p + sgen - load? Compute as ext_p - sum(load p_mw) + sum(sgen p_mw)
    total_load_p = net.load.p_mw.sum() if len(net.load)>0 else 0
    total_sgen_p = net.sgen.p_mw.sum() if len(net.sgen)>0 else 0
    # Losses = ext_p + sgen - load (since ext supplies net)
    losses_p = ext_p + total_sgen_p - total_load_p
    total_q = net.load.q_mvar.sum() if len(net.load)>0 else 0  # approx
    # line loading
    if len(net.res_line)>0:
        max_line_loading = net.res_line.loading_percent.max()
        worst_line_idx = net.res_line.loading_percent.idxmax()
        worst_line = net.line.name.iloc[worst_line_idx] if worst_line_idx in net.line.index else str(worst_line_idx)
        # also record p_from for reverse detection
        line_p = net.res_line.p_from_mw.to_dict()
    else:
        max_line_loading = 0
        worst_line="none"
        line_p={}
    if len(net.res_trafo)>0:
        max_trafo_loading = net.res_trafo.loading_percent.max()
        worst_trafo_idx = net.res_trafo.loading_percent.idxmax()
        worst_trafo = net.trafo.name.iloc[worst_trafo_idx] if worst_trafo_idx in net.trafo.index else str(worst_trafo_idx)
        trafo_p = net.res_trafo.p_hv_mw.to_dict() if 'p_hv_mw' in net.res_trafo.columns else {}
    else:
        max_trafo_loading=0
        worst_trafo="none"
        trafo_p={}
    return {
        "min_vm": float(min_vm), "max_vm": float(max_vm),
        "min_bus": str(min_bus_name), "max_bus": str(max_bus_name),
        "ext_p": ext_p, "ext_q": ext_q,
        "losses_p": float(losses_p),
        "total_load_p": float(total_load_p), "total_sgen_p": float(total_sgen_p),
        "max_line_loading": float(max_line_loading) if not pd.isna(max_line_loading) else 0,
        "worst_line": str(worst_line),
        "max_trafo_loading": float(max_trafo_loading) if not pd.isna(max_trafo_loading) else 0,
        "worst_trafo": str(worst_trafo),
        "vm_series": vm,  # for later pv_bus lookup
        "line_p": line_p,
        "trafo_p": trafo_p,
        "res_bus": net.res_bus.copy()
    }

def run_case(base_net_template, pv_bus_id, pv_kw_total):
    """Clone template, add sgen at pv_bus, run PF, return metrics or None if fails."""
    net = copy.deepcopy(base_net_template)
    # Add PV as sgen at LV bus
    pp_bus_idx = bus_name_to_idx(net, pv_bus_id)
    if pp_bus_idx is None:
        return None, f"bus {pv_bus_id} not found"
    if pv_kw_total > 0:
        # add sgen
        pp.create_sgen(net, bus=pp_bus_idx, p_mw=pv_kw_total/1000.0, q_mvar=0, name=f"PV_{pv_bus_id}_{pv_kw_total}kW", type="PV")
    try:
        pp.runpp(net, algorithm='nr', max_iteration=500, numba=False, tolerance_mva=1e-3, enforce_q_limits=False)
        if net.converged:
            metrics = extract_metrics(net)
            # also get pv_bus voltage
            pv_vm = float(net.res_bus.vm_pu.iloc[pp_bus_idx])
            metrics["pv_bus_vm"] = pv_vm
            metrics["net"] = net
            return metrics, None
        else:
            return None, "not converged"
    except Exception as e:
        return None, str(e)

# Load valid buses and select representative set
import csv
valid_buses=[]
with open(VALID_BUSES_CSV,'r') as f:
    r=csv.DictReader(f)
    for row in r:
        valid_buses.append(row)

# Pick representative buses systematic: ensure section coverage
# Sections: we want spread: Head, Main_720-734, Main_735-750, Branch_752-765, Delta, secondary
# Valid buses are all LV - we will sample every Nth
# Sort by bus_id numeric
valid_sorted = sorted(valid_buses, key=lambda x: int(x['bus_id']) if x['bus_id'].isdigit() else 9999)
# For Phase1, pick 15 representative buses covering range: choose evenly
# Indices: spread across 71
import math
n_pick = 15
step = len(valid_sorted)/n_pick
picked_buses = []
for i in range(n_pick):
    idx = int(i*step)
    picked_buses.append(valid_sorted[idx]['bus_id'])
# Ensure we include specific interesting: far end (770,772,734,743), strong (720), weak (756? but 756 is MV excluded, so LV 759,764)
# Override to include key LV buses with load: 770 (0.45MW load), 772, 743, 759, 748, 732
key_buses = ["708","712","720","728","739","743","748","756","759","764","769","770","772","620","714"]
# Use key_buses as primary if they are valid
picked_buses = [b for b in key_buses if b in [x['bus_id'] for x in valid_sorted]]
# Add few more to reach 15: add 730,732,740
for b in ["730","732","740","716","708"]:
    if b not in picked_buses and b in [x['bus_id'] for x in valid_sorted]:
        picked_buses.append(b)
picked_buses = picked_buses[:15]
print(f"Picked PV buses for Phase1: {picked_buses}")

# Define PV sizes
new_pv_options = [5, 30, 50, 100, 250]  # 5 sizes
existing_options_for_extra = [0, 5, 10]

# Build scenario list: 15 buses x 5 sizes =75 with existing=0
scenarios=[]
sid=1
for bus in picked_buses:
    for new_kw in new_pv_options:
        scenarios.append({"scenario_id": f"S{sid:03d}", "feeder_id": "IEEE_CompTestFeeder", "pv_bus": bus, "existing_pv_kw": 0, "new_pv_kw": new_kw, "total_pv_kw": new_kw})
        sid+=1
# Replace last 3 scenarios with existing variations to test BASE/PV separation (keep count 75, so drop 3 and add 3)
# Remove last 3
scenarios = scenarios[:-3]
# Add existing tests
for (bus, exist, new) in [("770",5,50), ("770",10,100), ("720",10,30)]:
    scenarios.append({"scenario_id": f"S{sid:03d}", "feeder_id": "IEEE_CompTestFeeder", "pv_bus": bus, "existing_pv_kw": exist, "new_pv_kw": new, "total_pv_kw": exist+new})
    sid+=1

print(f"Total scenarios: {len(scenarios)}")

# Now run each scenario with BASE/PV
base_net_template = pp.from_json(NET_PATH)

rows=[]
failed=[]
for sc in scenarios:
    pv_bus = sc["pv_bus"]
    exist = sc["existing_pv_kw"]
    new = sc["new_pv_kw"]
    total = sc["total_pv_kw"]
    pp_bus_idx = bus_name_to_idx(base_net_template, pv_bus)
    if pp_bus_idx is None:
        failed.append((sc["scenario_id"],"bus not found"))
        continue
    # BASE case: existing only
    base_metrics, err = run_case(base_net_template, pv_bus, exist)
    if base_metrics is None:
        failed.append((sc["scenario_id"], f"BASE failed: {err}"))
        # record failed row with NaNs
        rows.append({**sc, "converged": False, "fail_reason": f"BASE:{err}"})
        continue
    pv_metrics, err2 = run_case(base_net_template, pv_bus, total)
    if pv_metrics is None:
        failed.append((sc["scenario_id"], f"PV failed: {err2}"))
        rows.append({**sc, "converged": False, "fail_reason": f"PV:{err2}"})
        continue

    # Compute deltas
    base_pv_vm = base_metrics["pv_bus_vm"]
    pv_pv_vm = pv_metrics["pv_bus_vm"]
    delta_pv_vm = pv_pv_vm - base_pv_vm

    max_voltage_rise = pv_metrics["max_vm"] - base_metrics["max_vm"]
    # Also per location rise
    # Changes
    delta_ext_p = pv_metrics["ext_p"] - base_metrics["ext_p"]
    delta_ext_q = pv_metrics["ext_q"] - base_metrics["ext_q"]
    delta_losses = pv_metrics["losses_p"] - base_metrics["losses_p"]
    delta_line = pv_metrics["max_line_loading"] - base_metrics["max_line_loading"]
    delta_trafo = pv_metrics["max_trafo_loading"] - base_metrics["max_trafo_loading"]

    # Reverse power flow detection
    reverse = 0
    reverse_reason = ""
    # source reverse: pv ext_p negative (export) or large drop crossing zero
    if pv_metrics["ext_p"] < 0:
        reverse = 1
        reverse_reason = f"source export {pv_metrics['ext_p']:.3f}MW"
    elif base_metrics["ext_p"] > 0.5 and pv_metrics["ext_p"] < 0.2*base_metrics["ext_p"]:
        # Significant reduction but not export - not flagged as reverse in Phase1, only if negative
        pass
    # Check line flow sign flip for worst line (simplify)
    # Compare line_p dicts
    for lid, p_base in base_metrics["line_p"].items():
        p_pv = pv_metrics["line_p"].get(lid, 0)
        if p_base > 0.01 and p_pv < -0.01:
            reverse = 1
            reverse_reason += f"; line {lid} {p_base:.3f}->{p_pv:.3f}MW reversed"
            break
    # trafo reverse (e.g., LV to HV)
    for tid, p_base in base_metrics["trafo_p"].items():
        p_pv = pv_metrics["trafo_p"].get(tid, 0)
        if p_base > 0.01 and p_pv < -0.01:
            reverse = 1
            reverse_reason += f"; trafo {tid} reversed"
            break
    if reverse_reason=="":
        reverse_reason="none"

    # Constraint checks
    constraint_type="none"
    constraint_reason="No violation"
    # Hard voltage
    if pv_metrics["max_vm"] > V_HIGH_HARD:
        constraint_type="voltage"
        constraint_reason=f"Max voltage {pv_metrics['max_vm']:.4f} pu at bus {pv_metrics['max_bus']} exceeds {V_HIGH_HARD}"
    elif pv_metrics["min_vm"] < V_LOW_HARD:
        constraint_type="voltage"
        constraint_reason=f"Min voltage {pv_metrics['min_vm']:.4f} pu at bus {pv_metrics['min_bus']} below {V_LOW_HARD}"
    elif abs(delta_pv_vm) > V_RISE_HARD:
        constraint_type="voltage_rise"
        constraint_reason=f"Voltage rise at PV bus {pv_bus} {delta_pv_vm:.4f} pu exceeds {V_RISE_HARD}"
    elif pv_metrics["max_line_loading"] > LINE_HARD:
        constraint_type="line_loading"
        constraint_reason=f"Line {pv_metrics['worst_line']} loading {pv_metrics['max_line_loading']:.1f}% exceeds {LINE_HARD}%"
    elif pv_metrics["max_trafo_loading"] > TRAFO_HARD:
        constraint_type="transformer_loading"
        constraint_reason=f"Transformer {pv_metrics['worst_trafo']} loading {pv_metrics['max_trafo_loading']:.1f}% exceeds {TRAFO_HARD}%"
    else:
        constraint_type="none"
        constraint_reason="No hard violation"

    # Label
    label="SAFE"
    if constraint_type != "none":
        label="CONSTRAINED"
    else:
        # check caution bands
        caution=False
        caution_reasons=[]
        if pv_metrics["max_vm"] > V_HIGH_CAUTION:
            caution=True; caution_reasons.append(f"max {pv_metrics['max_vm']:.4f}>{V_HIGH_CAUTION}")
        if pv_metrics["min_vm"] < V_LOW_CAUTION:
            caution=True; caution_reasons.append(f"min {pv_metrics['min_vm']:.4f}<{V_LOW_CAUTION}")
        if abs(delta_pv_vm) >= V_RISE_CAUTION:
            caution=True; caution_reasons.append(f"rise {delta_pv_vm:.4f}>={V_RISE_CAUTION}")
        if pv_metrics["max_line_loading"] >= LINE_CAUTION:
            caution=True; caution_reasons.append(f"line {pv_metrics['max_line_loading']:.1f}>={LINE_CAUTION}%")
        if pv_metrics["max_trafo_loading"] >= TRAFO_CAUTION:
            caution=True; caution_reasons.append(f"trafo {pv_metrics['max_trafo_loading']:.1f}>={TRAFO_CAUTION}%")
        if reverse==1:
            caution=True; caution_reasons.append("reverse flow")
        if caution:
            label="CAUTION"
            constraint_type="caution"
            constraint_reason="; ".join(caution_reasons)

    # Build row for CSV
    # Get existing load at pv bus for reference
    pp_bus_idx = bus_name_to_idx(base_net_template, pv_bus)
    vn = base_net_template.bus.vn_kv.iloc[pp_bus_idx]
    # existing load at bus
    load_at_bus = base_net_template.load[base_net_template.load.bus==pp_bus_idx].p_mw.sum() if pp_bus_idx in base_net_template.load.bus.values else 0
    row = {
        "scenario_id": sc["scenario_id"],
        "feeder_id": sc["feeder_id"],
        "pv_bus": pv_bus,
        "pv_bus_pp_idx": pp_bus_idx,
        "pv_bus_vn_kv": vn,
        "existing_pv_kw": exist,
        "new_pv_kw": new,
        "total_pv_kw": total,
        "base_pv_bus_voltage_pu": round(base_pv_vm,5),
        "pv_pv_bus_voltage_pu": round(pv_pv_vm,5),
        "delta_pv_bus_voltage_pu": round(delta_pv_vm,5),
        "base_min_voltage_pu": round(base_metrics["min_vm"],5),
        "base_max_voltage_pu": round(base_metrics["max_vm"],5),
        "base_min_voltage_bus": base_metrics["min_bus"],
        "base_max_voltage_bus": base_metrics["max_bus"],
        "pv_min_voltage_pu": round(pv_metrics["min_vm"],5),
        "pv_max_voltage_pu": round(pv_metrics["max_vm"],5),
        "pv_min_voltage_bus": pv_metrics["min_bus"],
        "pv_max_voltage_bus": pv_metrics["max_bus"],
        "max_voltage_rise_pu": round(max_voltage_rise,5),
        "worst_voltage_bus": pv_metrics["max_bus"],
        "base_max_line_loading_pct": round(base_metrics["max_line_loading"],2),
        "pv_max_line_loading_pct": round(pv_metrics["max_line_loading"],2),
        "delta_line_loading_pct": round(delta_line,2),
        "worst_line": pv_metrics["worst_line"],
        "base_worst_line": base_metrics["worst_line"],
        "base_max_transformer_loading_pct": round(base_metrics["max_trafo_loading"],2),
        "pv_max_transformer_loading_pct": round(pv_metrics["max_trafo_loading"],2),
        "delta_transformer_loading_pct": round(delta_trafo,2),
        "worst_transformer": pv_metrics["worst_trafo"],
        "base_worst_transformer": base_metrics["worst_trafo"],
        "base_total_p_kw": round(base_metrics["ext_p"]*1000,2),
        "pv_total_p_kw": round(pv_metrics["ext_p"]*1000,2),
        "delta_total_p_kw": round(delta_ext_p*1000,2),
        "base_total_q_kvar": round(base_metrics["ext_q"]*1000,2),
        "pv_total_q_kvar": round(pv_metrics["ext_q"]*1000,2),
        "delta_total_q_kvar": round(delta_ext_q*1000,2),
        "base_losses_kw": round(base_metrics["losses_p"]*1000,2),
        "pv_losses_kw": round(pv_metrics["losses_p"]*1000,2),
        "delta_losses_kw": round(delta_losses*1000,2),
        "reverse_power_flow": reverse,
        "reverse_reason": reverse_reason,
        "existing_load_at_bus_kw": round(load_at_bus*1000,2),
        "constraint_type": constraint_type,
        "constraint_reason": constraint_reason,
        "label": label,
        "converged": True,
        "base_converged": True,
        "pv_converged": True
    }
    rows.append(row)

# Save CSV
if rows:
    # Ensure field order per spec
    fieldnames = ["scenario_id","feeder_id","pv_bus","existing_pv_kw","new_pv_kw","total_pv_kw",
                  "base_pv_bus_voltage_pu","pv_pv_bus_voltage_pu","delta_pv_bus_voltage_pu",
                  "base_min_voltage_pu","base_max_voltage_pu","pv_min_voltage_pu","pv_max_voltage_pu",
                  "max_voltage_rise_pu","worst_voltage_bus",
                  "base_max_line_loading_pct","pv_max_line_loading_pct","base_max_transformer_loading_pct","pv_max_transformer_loading_pct",
                  "worst_line","worst_transformer",
                  "base_total_p_kw","pv_total_p_kw","delta_total_p_kw",
                  "base_total_q_kvar","pv_total_q_kvar","delta_total_q_kvar",
                  "base_losses_kw","pv_losses_kw","delta_losses_kw",
                  "reverse_power_flow","constraint_type","constraint_reason","label",
                  # extras
                  "base_min_voltage_bus","base_max_voltage_bus","pv_min_voltage_bus","pv_max_voltage_bus",
                  "delta_line_loading_pct","delta_transformer_loading_pct","existing_load_at_bus_kw","pv_bus_vn_kv","base_worst_line","base_worst_transformer","reverse_reason","converged"]
    with open(OUTPUT_CSV,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            # filter to fieldnames
            out={k:r.get(k,"") for k in fieldnames}
            w.writerow(out)
    print(f"Saved {len(rows)} rows to {OUTPUT_CSV}")
    # also print label counts
    from collections import Counter
    c=Counter([r['label'] for r in rows])
    print("Label counts:", c)
    print(f"Failed: {len(failed)}", failed[:5])
    # Sanity quick stats
    deltas=[r['delta_pv_bus_voltage_pu'] for r in rows]
    print(f"Delta V range: {min(deltas):.5f} to {max(deltas):.5f} mean {np.mean(deltas):.5f}")
else:
    print("No rows generated")

