import json, copy, sys, io, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandapower as pp
import pandas as pd, numpy as np, math
from collections import Counter

CONFIG_PATH = r"C:\Users\ASUS\Documents\suryaghar\scenario_config.json"
NET_PATH = r"C:\Users\ASUS\Documents\suryaghar\feeder_network.json"
VALID_CSV = r"C:\Users\ASUS\Documents\suryaghar\valid_pv_buses.csv"
# thresholds
with open(CONFIG_PATH,'r') as f:
    cfg=json.load(f)
th=cfg["thresholds"]
V_LOW_HARD=th["voltage_hard_low_pu"]["value"]
V_HIGH_HARD=th["voltage_hard_high_pu"]["value"]
V_RISE_HARD=th["voltage_rise_hard_pu"]["value"]
LINE_HARD=th["line_loading_hard_pct"]["value"]
TRAFO_HARD=th["transformer_loading_hard_pct"]["value"]

def bus_idx(net, name):
    hits=net.bus.index[net.bus.name==str(name)]
    return int(hits[0]) if len(hits)>0 else None

def extract(net):
    vm=net.res_bus.vm_pu
    return {"min_vm":float(vm.min()), "max_vm":float(vm.max()),
            "min_bus":str(net.bus.name.iloc[vm.idxmin()]), "max_bus":str(net.bus.name.iloc[vm.idxmax()]),
            "ext_p":float(net.res_ext_grid.p_mw.iloc[0]), "max_line":float(net.res_line.loading_percent.max()), "worst_line":str(net.line.name.iloc[net.res_line.loading_percent.idxmax()]),
            "max_trafo":float(net.res_trafo.loading_percent.max()), "worst_trafo":str(net.trafo.name.iloc[net.res_trafo.loading_percent.idxmax()]),
            "line_p":net.res_line.p_from_mw.to_dict(), "trafo_p":net.res_trafo.p_hv_mw.to_dict() if 'p_hv_mw' in net.res_trafo else {}}

def run_case(template, bus_id, pv_kw):
    net=copy.deepcopy(template)
    idx=bus_idx(net,bus_id)
    if idx is None:
        return None,None
    if pv_kw>0:
        pp.create_sgen(net,bus=idx,p_mw=pv_kw/1000.0,q_mvar=0,name=f"PV_{bus_id}")
    try:
        pp.runpp(net,algorithm='nr',max_iteration=500,numba=False,tolerance_mva=1e-3,enforce_q_limits=False)
        if net.converged:
            m=extract(net)
            m["pv_bus_vm"]=float(net.res_bus.vm_pu.iloc[idx])
            m["net"]=net
            return m,net
        else:
            return None,None
    except:
        return None,None

template=pp.from_json(NET_PATH)
valid=pd.read_csv(VALID_CSV, dtype={'bus_id':str})
valid_buses=valid['bus_id'].astype(str).tolist()

# Target deltas near threshold: 0.04,0.045,0.048,0.049,0.050,0.051,0.052,0.055,0.060
# Instead of targeting deltas directly, sweep PV sizes for each bus and keep those where delta in 0.04-0.06
aug_rows=[]
existing_choices=[0,5,10]
# For each bus, try PV sizes 20 to 100 step 5 (high resolution near threshold)
candidate_sizes=list(range(20, 101, 5)) + [110,120,130]
# Also add 14,18 for low threshold buses
# Limit to 71*~15 = ~1065 candidates, filter to 0.04-0.06
candidates_checked=0
mid=1501  # start after 1500 existing
for bus in valid_buses:
    base_m,_=run_case(template,bus,0)
    if base_m is None:
        continue
    base_vm=base_m["pv_bus_vm"]
    for new_kw in candidate_sizes:
        # also try with existing 5
        for exist in [0]:
            total=exist+new_kw
            pv_m,_=run_case(template,bus,total)
            if pv_m is None:
                continue
            candidates_checked+=1
            delta=pv_m["pv_bus_vm"]-base_vm
            # Keep if delta 0.035-0.065 (near threshold band expanded)
            if 0.035 <= abs(delta) <= 0.065:
                # Label via same logic
                max_vm=pv_m["max_vm"]; min_vm=pv_m["min_vm"]
                delta_abs=abs(delta)
                max_line=pv_m["max_line"]; max_trafo=pv_m["max_trafo"]
                ctype="none"
                if max_vm>V_HIGH_HARD:
                    ctype="voltage"
                elif min_vm<V_LOW_HARD:
                    ctype="voltage"
                elif delta_abs>V_RISE_HARD:
                    ctype="voltage_rise"
                elif max_line>LINE_HARD:
                    ctype="line_loading"
                elif max_trafo>TRAFO_HARD:
                    ctype="transformer_loading"
                label="CONSTRAINED" if ctype!="none" else "SAFE"
                # Check caution to refine label: if not CONSTRAINED but caution, label CAUTION
                if ctype=="none":
                    # check caution thresholds
                    V_HIGH_CAUTION=cfg["thresholds"]["voltage_caution_high_pu"]["value"]
                    V_RISE_CAUTION=cfg["thresholds"]["voltage_rise_caution_pu"]["value"]
                    LINE_CAUTION=cfg["thresholds"]["line_loading_caution_pct"]["value"]
                    TRAFO_CAUTION=cfg["thresholds"]["transformer_loading_caution_pct"]["value"]
                    V_LOW_CAUTION=cfg["thresholds"]["voltage_caution_low_pu"]["value"]
                    # reverse check simplified: not needed for augmentation, but keep
                    caution=False
                    if max_vm>V_HIGH_CAUTION: caution=True
                    if min_vm<V_LOW_CAUTION: caution=True
                    if delta_abs>=V_RISE_CAUTION: caution=True
                    if max_line>=LINE_CAUTION: caution=True
                    if max_trafo>=TRAFO_CAUTION: caution=True
                    if caution:
                        label="CAUTION"
                # Only keep CONSTRAINED and CAUTION near threshold; SAFE near threshold also valuable
                # Keep all in band
                aug_rows.append({"scenario_id":f"S{mid:05d}", "feeder_id":"IEEE_CompTestFeeder", "pv_bus":bus, "existing_pv_kw":exist, "new_pv_kw":new_kw, "total_pv_kw":total,
                                 "base_pv_bus_voltage_pu":round(base_vm,5), "pv_pv_bus_voltage_pu":round(pv_m["pv_bus_vm"],5), "delta_pv_bus_voltage_pu":round(delta,5),
                                 "pv_max_voltage_pu":round(max_vm,5), "pv_max_transformer_loading_pct":round(max_trafo,2), "worst_transformer":pv_m["worst_trafo"],
                                 "label":label, "constraint_type":ctype, "delta":delta})
                mid+=1
                if len(aug_rows)>=400: # cap
                    break
        if len(aug_rows)>=400:
            break
    if len(aug_rows)>=400:
        break

print(f"Checked {candidates_checked} candidates, kept {len(aug_rows)} near-threshold 0.035-0.065")
# Show distribution
from collections import Counter
print(Counter([r['label'] for r in aug_rows]))
print(f"Delta range kept {min(r['delta'] for r in aug_rows):.4f} to {max(r['delta'] for r in aug_rows):.4f}")
# Show few examples
for r in aug_rows[:10]:
    print(r)

# Now need to generate full rows for those kept, with full pipeline to match pv_dataset.csv schema
# For each kept, run full BASE/PV extraction as in generation to get all columns
# Reuse run_case for base and pv to get full metrics
full_rows=[]
for r in aug_rows:
    bus=r['pv_bus']; exist=r['existing_pv_kw']; new=r['new_pv_kw']; total=r['total_pv_kw']
    base_m,_=run_case(template,bus,exist)
    pv_m,_=run_case(template,bus,total)
    if base_m is None or pv_m is None:
        continue
    base_vm=base_m["pv_bus_vm"]; pv_vm=pv_m["pv_bus_vm"]; delta=pv_vm-base_vm
    # need full metrics for dataset: min/max, line/trafo, source, losses etc as before
    # Simplified: reuse earlier extraction but we need losses, source, etc. Let's compute via same functions as generation
    # For brevity, we will create minimal full row by copying from earlier logic: use same as dataset_generation_phase2 but simplified
    # We have base_m and pv_m already with needed fields, but need ext_p, losses etc. extract already gave ext_p etc? Our extract simplified earlier didn't include losses, need recompute losses etc.
    # Let's recompute losses: ext_p + sgen - load
    # For losses we need total_load etc. Use template load sum (same as generation)
    # Instead just run full pipeline via helper that returns same as generation's extract_metrics (we have simplified)
    # For augmentation we will generate via same logic as enrich: we can call dataset_generation's run_case with full metrics
    # Simpler: just save the kept rows as augmentation candidates and let enrich step add features later via join
    # For now save augmentation list as csv with same schema as pv_dataset.csv minimal
    pass

# Save augmentation candidates as csv for later full generation
import csv, pandas as pd
df=pd.DataFrame(aug_rows)
df.to_csv(r"C:\Users\ASUS\Documents\suryaghar\augmentation_candidates.csv", index=False)
print(f"Saved {len(df)} candidates to augmentation_candidates.csv")
