import json, copy, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandapower as pp
import pandas as pd, numpy as np, math

CONFIG_PATH = r"C:\Users\ASUS\Documents\suryaghar\scenario_config.json"
NET_PATH = r"C:\Users\ASUS\Documents\suryaghar\feeder_network.json"

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

def bus_idx(net, name):
    hits=net.bus.index[net.bus.name==str(name)]
    return int(hits[0]) if len(hits)>0 else None

def extract_metrics(net):
    vm=net.res_bus.vm_pu
    min_vm=float(vm.min()); max_vm=float(vm.max())
    min_bus=str(net.bus.name.iloc[vm.idxmin()]); max_bus=str(net.bus.name.iloc[vm.idxmax()])
    ext_p=float(net.res_ext_grid.p_mw.iloc[0]); ext_q=float(net.res_ext_grid.q_mvar.iloc[0])
    total_load_p=float(net.load.p_mw.sum()); total_sgen_p=float(net.sgen.p_mw.sum())
    losses_p=ext_p+total_sgen_p-total_load_p
    max_line=float(net.res_line.loading_percent.max()) if len(net.res_line)>0 else 0
    worst_line=str(net.line.name.iloc[net.res_line.loading_percent.idxmax()]) if len(net.res_line)>0 else "none"
    max_trafo=float(net.res_trafo.loading_percent.max()) if len(net.res_trafo)>0 else 0
    worst_trafo=str(net.trafo.name.iloc[net.res_trafo.loading_percent.idxmax()]) if len(net.res_trafo)>0 else "none"
    line_p=net.res_line.p_from_mw.to_dict() if len(net.res_line)>0 else {}
    trafo_p=net.res_trafo.p_hv_mw.to_dict() if len(net.res_trafo)>0 and 'p_hv_mw' in net.res_trafo else {}
    return {"min_vm":min_vm,"max_vm":max_vm,"min_bus":min_bus,"max_bus":max_bus,"ext_p":ext_p,"ext_q":ext_q,"losses_p":losses_p,
            "max_line":max_line,"worst_line":worst_line,"max_trafo":max_trafo,"worst_trafo":worst_trafo,"line_p":line_p,"trafo_p":trafo_p, "vm":vm}

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
            m=extract_metrics(net)
            m["pv_bus_vm"]=float(net.res_bus.vm_pu.iloc[idx])
            m["net"]=net
            return m,net
        else:
            return None,None
    except:
        return None,None

template=pp.from_json(NET_PATH)
cand=pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\augmentation_candidates.csv", dtype={'pv_bus':str})
print(f"Candidates {len(cand)}")

rows=[]
for _,r in cand.iterrows():
    bus=str(r['pv_bus']); exist=int(r['existing_pv_kw']); new=int(r['new_pv_kw']); total=int(r['total_pv_kw'])
    base_m,_=run_case(template,bus,exist)
    pv_m,_=run_case(template,bus,total)
    if base_m is None or pv_m is None:
        continue
    base_vm=base_m["pv_bus_vm"]; pv_vm=pv_m["pv_bus_vm"]; delta=pv_vm-base_vm
    max_rise=pv_m["max_vm"]-base_m["max_vm"]
    delta_ext_p=pv_m["ext_p"]-base_m["ext_p"]; delta_ext_q=pv_m["ext_q"]-base_m["ext_q"]
    delta_losses=pv_m["losses_p"]-base_m["losses_p"]
    delta_line=pv_m["max_line"]-base_m["max_line"]
    delta_trafo=pv_m["max_trafo"]-base_m["max_trafo"]
    reverse=0; rev_reason="none"
    if pv_m["ext_p"]<0:
        reverse=1; rev_reason=f"source export {pv_m['ext_p']:.3f}MW"
    else:
        for lid,pb in base_m["line_p"].items():
            ppv=pv_m["line_p"].get(lid,0)
            if pb>0.01 and ppv<-0.01:
                reverse=1; rev_reason=f"line {lid} reversed"; break
        if reverse==0:
            for tid,pb in base_m["trafo_p"].items():
                ppv=pv_m["trafo_p"].get(tid,0)
                if pb>0.01 and ppv<-0.01:
                    reverse=1; rev_reason=f"trafo {tid} reversed"; break
    ctype="none"; creason="No violation"
    if pv_m["max_vm"]>V_HIGH_HARD:
        ctype="voltage"; creason=f"Max voltage {pv_m['max_vm']:.4f} at {pv_m['max_bus']} exceeds {V_HIGH_HARD}"
    elif pv_m["min_vm"]<V_LOW_HARD:
        ctype="voltage"; creason=f"Min {pv_m['min_vm']:.4f} below {V_LOW_HARD}"
    elif abs(delta)>V_RISE_HARD:
        ctype="voltage_rise"; creason=f"Voltage rise at PV bus {bus} {delta:.4f} pu exceeds {V_RISE_HARD}"
    elif pv_m["max_line"]>LINE_HARD:
        ctype="line_loading"; creason=f"Line {pv_m['worst_line']} {pv_m['max_line']:.1f}%"
    elif pv_m["max_trafo"]>TRAFO_HARD:
        ctype="transformer_loading"; creason=f"Transformer {pv_m['worst_trafo']} {pv_m['max_trafo']:.1f}%"
    label="SAFE"
    if ctype!="none":
        label="CONSTRAINED"
    else:
        caution=False; creasons=[]
        if pv_m["max_vm"]>V_HIGH_CAUTION: caution=True; creasons.append(f"max {pv_m['max_vm']:.4f}>{V_HIGH_CAUTION}")
        if pv_m["min_vm"]<V_LOW_CAUTION: caution=True; creasons.append(f"min {pv_m['min_vm']:.4f}<{V_LOW_CAUTION}")
        if abs(delta)>=V_RISE_CAUTION: caution=True; creasons.append(f"rise {delta:.4f}>={V_RISE_CAUTION}")
        if pv_m["max_line"]>=LINE_CAUTION: caution=True; creasons.append(f"line {pv_m['max_line']:.1f}>={LINE_CAUTION}%")
        if pv_m["max_trafo"]>=TRAFO_CAUTION: caution=True; creasons.append(f"trafo {pv_m['max_trafo']:.1f}>={TRAFO_CAUTION}%")
        if reverse==1: caution=True; creasons.append("reverse flow")
        if caution:
            label="CAUTION"; ctype="caution"; creason="; ".join(creasons)
    # existing load
    pp_idx=bus_idx(template,bus)
    vn=template.bus.vn_kv.iloc[pp_idx]
    load_at=template.load[template.load.bus==pp_idx].p_mw.sum() if pp_idx in template.load.bus.values else 0
    row={"scenario_id":r['scenario_id'],"feeder_id":"IEEE_CompTestFeeder","pv_bus":bus,"existing_pv_kw":exist,"new_pv_kw":new,"total_pv_kw":total,
         "base_pv_bus_voltage_pu":round(base_vm,5),"pv_pv_bus_voltage_pu":round(pv_vm,5),"delta_pv_bus_voltage_pu":round(delta,5),
         "base_min_voltage_pu":round(base_m["min_vm"],5),"base_max_voltage_pu":round(base_m["max_vm"],5),"base_min_voltage_bus":base_m["min_bus"],"base_max_voltage_bus":base_m["max_bus"],
         "pv_min_voltage_pu":round(pv_m["min_vm"],5),"pv_max_voltage_pu":round(pv_m["max_vm"],5),"pv_min_voltage_bus":pv_m["min_bus"],"pv_max_voltage_bus":pv_m["max_bus"],
         "max_voltage_rise_pu":round(max_rise,5),"worst_voltage_bus":pv_m["max_bus"],
         "base_max_line_loading_pct":round(base_m["max_line"],2),"pv_max_line_loading_pct":round(pv_m["max_line"],2),"delta_line_loading_pct":round(delta_line,2),"worst_line":pv_m["worst_line"],"base_worst_line":base_m["worst_line"],
         "base_max_transformer_loading_pct":round(base_m["max_trafo"],2),"pv_max_transformer_loading_pct":round(pv_m["max_trafo"],2),"delta_transformer_loading_pct":round(delta_trafo,2),"worst_transformer":pv_m["worst_trafo"],"base_worst_transformer":base_m["worst_trafo"],
         "base_total_p_kw":round(base_m["ext_p"]*1000,2),"pv_total_p_kw":round(pv_m["ext_p"]*1000,2),"delta_total_p_kw":round(delta_ext_p*1000,2),
         "base_total_q_kvar":round(base_m["ext_q"]*1000,2),"pv_total_q_kvar":round(pv_m["ext_q"]*1000,2),"delta_total_q_kvar":round(delta_ext_q*1000,2),
         "base_losses_kw":round(base_m["losses_p"]*1000,2),"pv_losses_kw":round(pv_m["losses_p"]*1000,2),"delta_losses_kw":round(delta_losses*1000,2),
         "reverse_power_flow":reverse,"reverse_reason":rev_reason,"existing_load_at_bus_kw":round(load_at*1000,2),"pv_bus_vn_kv":vn,
         "constraint_type":ctype,"constraint_reason":creason,"label":label,"converged":True}
    rows.append(row)

df_aug=pd.DataFrame(rows)
print(f"Generated full rows {len(df_aug)}")
print(df_aug['label'].value_counts().to_dict())
# Merge with original pv_dataset.csv
orig=pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\pv_dataset.csv", dtype={'pv_bus':str})
combined=pd.concat([orig, df_aug], ignore_index=True)
# Deduplicate by (pv_bus,existing,new) keep first
combined['key']=combined['pv_bus'].astype(str)+"_"+combined['existing_pv_kw'].astype(str)+"_"+combined['new_pv_kw'].astype(str)
combined=combined.drop_duplicates(subset=['key'], keep='first')
combined=combined.drop(columns=['key'])
print(f"Original {len(orig)} + aug {len(df_aug)} => combined {len(combined)} unique")
combined.to_csv(r"C:\Users\ASUS\Documents\suryaghar\pv_dataset_augmented.csv", index=False)
print("Saved pv_dataset_augmented.csv")
# Also save enriched version will be generated next via enrich script on combined
