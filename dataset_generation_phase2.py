"""
Phase 2 Large Dataset - seeded, continuous sampling, cached BASE
"""
import json, copy, csv, sys, io, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandapower as pp
import pandas as pd
import numpy as np
from collections import Counter

CONFIG_PATH = r"C:\Users\ASUS\Documents\suryaghar\scenario_config.json"
NET_PATH = r"C:\Users\ASUS\Documents\suryaghar\feeder_network.json"
VALID_BUSES_CSV = r"C:\Users\ASUS\Documents\suryaghar\valid_pv_buses.csv"
OUTPUT_CSV = r"C:\Users\ASUS\Documents\suryaghar\pv_dataset.csv"

with open(CONFIG_PATH,'r') as f:
    cfg=json.load(f)
th=cfg["thresholds"]
V_LOW_HARD=th["voltage_hard_low_pu"]["value"]
V_HIGH_HARD=th["voltage_hard_high_pu"]["value"]
V_LOW_CAUTION=th["voltage_caution_low_pu"]["value"]
V_HIGH_CAUTION=th["voltage_caution_high_pu"]["value"]
V_RISE_HARD=th["voltage_rise_hard_pu"]["value"]
V_RISE_CAUTION=th["voltage_rise_caution_pu"]["value"]
LINE_HARD=th["line_loading_hard_pct"]["value"]
LINE_CAUTION=th["line_loading_caution_pct"]["value"]
TRAFO_HARD=th["transformer_loading_hard_pct"]["value"]
TRAFO_CAUTION=th["transformer_loading_caution_pct"]["value"]

SEED=42
random.seed(SEED)
np.random.seed(SEED)
TARGET_N=1500

valid_buses=[]
import csv as csvm
with open(VALID_BUSES_CSV,'r') as f:
    for row in csvm.DictReader(f):
        valid_buses.append(row['bus_id'])
print(f"Valid buses: {len(valid_buses)}")

scenarios=[]
seen=set()
attempts=0
mid=0
while len(scenarios)<TARGET_N and attempts < TARGET_N*5:
    attempts+=1
    bus = random.choice(valid_buses)
    r=random.random()
    if r<0.70:
        exist=0
    else:
        exist=random.randint(3,15)
    new=random.randint(5,250)
    key=(bus,exist,new)
    if key in seen:
        continue
    seen.add(key)
    mid+=1
    scenarios.append({"scenario_id": f"S{mid:05d}", "feeder_id":"IEEE_CompTestFeeder", "pv_bus":bus, "existing_pv_kw":exist, "new_pv_kw":new, "total_pv_kw":exist+new})
print(f"Generated {len(scenarios)} unique scenarios after {attempts} attempts seed {SEED}")
c_bus=Counter([s["pv_bus"] for s in scenarios])
print(f"Per-bus min {min(c_bus.values())} max {max(c_bus.values())} mean {np.mean(list(c_bus.values())):.1f}")
print(f"New range {min(s['new_pv_kw'] for s in scenarios)}-{max(s['new_pv_kw'] for s in scenarios)}")
print(f"Existing zeros {sum(1 for s in scenarios if s['existing_pv_kw']==0)}")

def bus_name_to_idx(net, bus_id_str):
    hits = net.bus.index[net.bus.name == str(bus_id_str)].tolist()
    return hits[0] if hits else None

def extract_metrics(net):
    vm = net.res_bus.vm_pu
    min_vm = vm.min(); max_vm = vm.max()
    min_bus = net.bus.name.iloc[vm.idxmin()]; max_bus = net.bus.name.iloc[vm.idxmax()]
    ext_p = float(net.res_ext_grid.p_mw.iloc[0]) if len(net.res_ext_grid)>0 else 0
    ext_q = float(net.res_ext_grid.q_mvar.iloc[0]) if len(net.res_ext_grid)>0 else 0
    total_load_p = net.load.p_mw.sum() if len(net.load)>0 else 0
    total_sgen_p = net.sgen.p_mw.sum() if len(net.sgen)>0 else 0
    losses_p = ext_p + total_sgen_p - total_load_p
    if len(net.res_line)>0:
        max_line = net.res_line.loading_percent.max()
        worst_line = net.line.name.iloc[net.res_line.loading_percent.idxmax()]
        line_p = net.res_line.p_from_mw.to_dict()
    else:
        max_line=0; worst_line="none"; line_p={}
    if len(net.res_trafo)>0:
        max_trafo = net.res_trafo.loading_percent.max()
        worst_trafo = net.trafo.name.iloc[net.res_trafo.loading_percent.idxmax()]
        trafo_p = net.res_trafo.p_hv_mw.to_dict() if 'p_hv_mw' in net.res_trafo.columns else {}
    else:
        max_trafo=0; worst_trafo="none"; trafo_p={}
    return {"min_vm":float(min_vm),"max_vm":float(max_vm),"min_bus":str(min_bus),"max_bus":str(max_bus),
            "ext_p":ext_p,"ext_q":ext_q,"losses_p":float(losses_p),"total_load_p":float(total_load_p),"total_sgen_p":float(total_sgen_p),
            "max_line_loading":float(max_line) if not pd.isna(max_line) else 0,"worst_line":str(worst_line),
            "max_trafo_loading":float(max_trafo) if not pd.isna(max_trafo) else 0,"worst_trafo":str(worst_trafo),
            "line_p":line_p,"trafo_p":trafo_p}

def run_case(template, pv_bus_id, pv_kw_total):
    net=copy.deepcopy(template)
    idx=bus_name_to_idx(net, pv_bus_id)
    if idx is None:
        return None,"bus not found"
    if pv_kw_total>0:
        pp.create_sgen(net,bus=idx,p_mw=pv_kw_total/1000.0,q_mvar=0,name=f"PV_{pv_bus_id}_{pv_kw_total}kW",type="PV")
    try:
        pp.runpp(net,algorithm='nr',max_iteration=500,numba=False,tolerance_mva=1e-3,enforce_q_limits=False)
        if net.converged:
            m=extract_metrics(net)
            m["pv_bus_vm"]=float(net.res_bus.vm_pu.iloc[idx])
            return m,None
        else:
            return None,"not converged"
    except Exception as e:
        return None,str(e)

template = pp.from_json(NET_PATH)
# cache base per (bus,existing) - do NOT share zero across buses because pv_bus_vm differs
base_cache={}
print("Base cache init (no shared zero)")

# helper to get base with correct pv_bus_vm lookup
def get_base_metrics(bus_id, exist_kw):
    key=(bus_id, exist_kw)
    if key in base_cache:
        return base_cache[key]
    m,err=run_case(template,bus_id,exist_kw)
    if m is None:
        return None
    base_cache[key]=m
    return m

rows=[]
failed=[]
for sc in scenarios:
    bus=sc["pv_bus"]; exist=sc["existing_pv_kw"]; new=sc["new_pv_kw"]; total=sc["total_pv_kw"]
    key=(bus,exist)
    if key in base_cache:
        base_m=base_cache[key]
    else:
        base_m,err=run_case(template,bus,exist)
        if base_m is None:
            failed.append((sc["scenario_id"],f"BASE {err}"))
            continue
        base_cache[key]=base_m
    pv_m,err2=run_case(template,bus,total)
    if pv_m is None:
        failed.append((sc["scenario_id"],f"PV {err2}"))
        continue
    base_pv_vm=base_m["pv_bus_vm"]; pv_pv_vm=pv_m["pv_bus_vm"]; delta_pv_vm=pv_pv_vm-base_pv_vm
    max_rise=pv_m["max_vm"]-base_m["max_vm"]
    delta_ext_p=pv_m["ext_p"]-base_m["ext_p"]; delta_ext_q=pv_m["ext_q"]-base_m["ext_q"]
    delta_losses=pv_m["losses_p"]-base_m["losses_p"]
    delta_line=pv_m["max_line_loading"]-base_m["max_line_loading"]
    delta_trafo=pv_m["max_trafo_loading"]-base_m["max_trafo_loading"]
    reverse=0; rev_reason="none"
    if pv_m["ext_p"]<0:
        reverse=1; rev_reason=f"source export {pv_m['ext_p']:.3f}MW"
    for lid,pb in base_m["line_p"].items():
        ppv=pv_m["line_p"].get(lid,0)
        if pb>0.01 and ppv<-0.01:
            reverse=1; rev_reason=f"line {lid} {pb:.3f}->{ppv:.3f} reversed"; break
    if reverse==0:
        for tid,pb in base_m["trafo_p"].items():
            ppv=pv_m["trafo_p"].get(tid,0)
            if pb>0.01 and ppv<-0.01:
                reverse=1; rev_reason=f"trafo {tid} reversed"; break
    if rev_reason=="none":
        rev_reason="none"
    ctype="none"; creason="No violation"
    if pv_m["max_vm"]>V_HIGH_HARD:
        ctype="voltage"; creason=f"Max voltage {pv_m['max_vm']:.4f} pu at bus {pv_m['max_bus']} exceeds {V_HIGH_HARD}"
    elif pv_m["min_vm"]<V_LOW_HARD:
        ctype="voltage"; creason=f"Min voltage {pv_m['min_vm']:.4f} pu at bus {pv_m['min_bus']} below {V_LOW_HARD}"
    elif abs(delta_pv_vm)>V_RISE_HARD:
        ctype="voltage_rise"; creason=f"Voltage rise at PV bus {bus} {delta_pv_vm:.4f} pu exceeds {V_RISE_HARD}"
    elif pv_m["max_line_loading"]>LINE_HARD:
        ctype="line_loading"; creason=f"Line {pv_m['worst_line']} loading {pv_m['max_line_loading']:.1f}% exceeds {LINE_HARD}%"
    elif pv_m["max_trafo_loading"]>TRAFO_HARD:
        ctype="transformer_loading"; creason=f"Transformer {pv_m['worst_trafo']} loading {pv_m['max_trafo_loading']:.1f}% exceeds {TRAFO_HARD}%"
    label="SAFE"
    if ctype!="none":
        label="CONSTRAINED"
    else:
        caution=False; creasons=[]
        if pv_m["max_vm"]>V_HIGH_CAUTION:
            caution=True; creasons.append(f"max {pv_m['max_vm']:.4f}>{V_HIGH_CAUTION}")
        if pv_m["min_vm"]<V_LOW_CAUTION:
            caution=True; creasons.append(f"min {pv_m['min_vm']:.4f}<{V_LOW_CAUTION}")
        if abs(delta_pv_vm)>=V_RISE_CAUTION:
            caution=True; creasons.append(f"rise {delta_pv_vm:.4f}>={V_RISE_CAUTION}")
        if pv_m["max_line_loading"]>=LINE_CAUTION:
            caution=True; creasons.append(f"line {pv_m['max_line_loading']:.1f}>={LINE_CAUTION}%")
        if pv_m["max_trafo_loading"]>=TRAFO_CAUTION:
            caution=True; creasons.append(f"trafo {pv_m['max_trafo_loading']:.1f}>={TRAFO_CAUTION}%")
        if reverse==1:
            caution=True; creasons.append("reverse flow")
        if caution:
            label="CAUTION"; ctype="caution"; creason="; ".join(creasons)
    pp_idx=bus_name_to_idx(template,bus)
    vn=template.bus.vn_kv.iloc[pp_idx]
    load_at=template.load[template.load.bus==pp_idx].p_mw.sum() if pp_idx in template.load.bus.values else 0
    row={"scenario_id":sc["scenario_id"],"feeder_id":sc["feeder_id"],"pv_bus":bus,"pp_bus_idx":pp_idx,"pv_bus_vn_kv":vn,
         "existing_pv_kw":exist,"new_pv_kw":new,"total_pv_kw":total,
         "base_pv_bus_voltage_pu":round(base_pv_vm,5),"pv_pv_bus_voltage_pu":round(pv_pv_vm,5),"delta_pv_bus_voltage_pu":round(delta_pv_vm,5),
         "base_min_voltage_pu":round(base_m["min_vm"],5),"base_max_voltage_pu":round(base_m["max_vm"],5),"base_min_voltage_bus":base_m["min_bus"],"base_max_voltage_bus":base_m["max_bus"],
         "pv_min_voltage_pu":round(pv_m["min_vm"],5),"pv_max_voltage_pu":round(pv_m["max_vm"],5),"pv_min_voltage_bus":pv_m["min_bus"],"pv_max_voltage_bus":pv_m["max_bus"],
         "max_voltage_rise_pu":round(max_rise,5),"worst_voltage_bus":pv_m["max_bus"],
         "base_max_line_loading_pct":round(base_m["max_line_loading"],2),"pv_max_line_loading_pct":round(pv_m["max_line_loading"],2),"delta_line_loading_pct":round(delta_line,2),"worst_line":pv_m["worst_line"],"base_worst_line":base_m["worst_line"],
         "base_max_transformer_loading_pct":round(base_m["max_trafo_loading"],2),"pv_max_transformer_loading_pct":round(pv_m["max_trafo_loading"],2),"delta_transformer_loading_pct":round(delta_trafo,2),"worst_transformer":pv_m["worst_trafo"],"base_worst_transformer":base_m["worst_trafo"],
         "base_total_p_kw":round(base_m["ext_p"]*1000,2),"pv_total_p_kw":round(pv_m["ext_p"]*1000,2),"delta_total_p_kw":round(delta_ext_p*1000,2),
         "base_total_q_kvar":round(base_m["ext_q"]*1000,2),"pv_total_q_kvar":round(pv_m["ext_q"]*1000,2),"delta_total_q_kvar":round(delta_ext_q*1000,2),
         "base_losses_kw":round(base_m["losses_p"]*1000,2),"pv_losses_kw":round(pv_m["losses_p"]*1000,2),"delta_losses_kw":round(delta_losses*1000,2),
         "reverse_power_flow":reverse,"reverse_reason":rev_reason,"existing_load_at_bus_kw":round(load_at*1000,2),
         "constraint_type":ctype,"constraint_reason":creason,"label":label,"converged":True}
    rows.append(row)
    if len(rows)%250==0:
        print(f"Progress {len(rows)}/{len(scenarios)} failed {len(failed)} cache {len(base_cache)}")

fieldnames=["scenario_id","feeder_id","pv_bus","existing_pv_kw","new_pv_kw","total_pv_kw",
            "base_pv_bus_voltage_pu","pv_pv_bus_voltage_pu","delta_pv_bus_voltage_pu",
            "base_min_voltage_pu","base_max_voltage_pu","pv_min_voltage_pu","pv_max_voltage_pu",
            "max_voltage_rise_pu","worst_voltage_bus",
            "base_max_line_loading_pct","pv_max_line_loading_pct","base_max_transformer_loading_pct","pv_max_transformer_loading_pct",
            "worst_line","worst_transformer",
            "base_total_p_kw","pv_total_p_kw","delta_total_p_kw",
            "base_total_q_kvar","pv_total_q_kvar","delta_total_q_kvar",
            "base_losses_kw","pv_losses_kw","delta_losses_kw",
            "reverse_power_flow","constraint_type","constraint_reason","label",
            "base_min_voltage_bus","base_max_voltage_bus","pv_min_voltage_bus","pv_max_voltage_bus",
            "delta_line_loading_pct","delta_transformer_loading_pct","existing_load_at_bus_kw","pv_bus_vn_kv","base_worst_line","base_worst_transformer","reverse_reason","converged"]
with open(OUTPUT_CSV,'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=fieldnames)
    w.writeheader()
    for r in rows:
        w.writerow({k:r.get(k,"") for k in fieldnames})
print(f"Saved {len(rows)} rows to {OUTPUT_CSV}, failed {len(failed)}")
print(Counter([r['label'] for r in rows]))
print(f"Seed {SEED}, continuous 5-250 new, 0-15 exist, deduped {len(rows)}")
