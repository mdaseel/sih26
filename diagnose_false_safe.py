import json, copy, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandapower as pp
import pandas as pd
import pickle

CONFIG_PATH = r"C:\Users\ASUS\Documents\suryaghar\scenario_config.json"
NET_PATH = r"C:\Users\ASUS\Documents\suryaghar\feeder_network.json"
VALID_BUSES_CSV = r"C:\Users\ASUS\Documents\suryaghar\valid_pv_buses.csv"

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
        worst_line_idx = net.res_line.loading_percent.idxmax()
        worst_line = net.line.name.iloc[worst_line_idx]
        # also get all line loadings for report
        line_loadings = net.res_line.loading_percent.to_dict()
        line_p = net.res_line.p_from_mw.to_dict()
    else:
        max_line=0; worst_line="none"; line_loadings={}; line_p={}
    if len(net.res_trafo)>0:
        max_trafo = net.res_trafo.loading_percent.max()
        worst_trafo_idx = net.res_trafo.loading_percent.idxmax()
        worst_trafo = net.trafo.name.iloc[worst_trafo_idx]
        trafo_loadings = net.res_trafo.loading_percent.to_dict()
        trafo_p = net.res_trafo.p_hv_mw.to_dict() if 'p_hv_mw' in net.res_trafo.columns else {}
    else:
        max_trafo=0; worst_trafo="none"; trafo_loadings={}; trafo_p={}
    return {"min_vm":float(min_vm),"max_vm":float(max_vm),"min_bus":str(min_bus),"max_bus":str(max_bus),
            "ext_p":ext_p,"ext_q":ext_q,"losses_p":float(losses_p),"vm":vm,
            "max_line":float(max_line) if not pd.isna(max_line) else 0,"worst_line":str(worst_line),"line_loadings":line_loadings,"line_p":line_p,
            "max_trafo":float(max_trafo) if not pd.isna(max_trafo) else 0,"worst_trafo":str(worst_trafo),"trafo_loadings":trafo_loadings,"trafo_p":trafo_p,
            "res_bus":net.res_bus.copy(), "res_trafo":net.res_trafo.copy(), "res_line":net.res_line.copy()}

def run_case(template, pv_bus_id, pv_kw_total):
    net=copy.deepcopy(template)
    idx=bus_name_to_idx(net, pv_bus_id)
    if idx is None:
        return None,None,"bus not found"
    if pv_kw_total>0:
        pp.create_sgen(net,bus=idx,p_mw=pv_kw_total/1000.0,q_mvar=0,name=f"PV_{pv_bus_id}_{pv_kw_total}kW",type="PV")
    try:
        pp.runpp(net,algorithm='nr',max_iteration=500,numba=False,tolerance_mva=1e-3,enforce_q_limits=False)
        if net.converged:
            m=extract_metrics(net)
            m["pv_bus_vm"]=float(net.res_bus.vm_pu.iloc[idx])
            m["net"]=net
            m["bus_idx"]=idx
            return m,net,None
        else:
            return None,None,"not converged"
    except Exception as e:
        return None,None,str(e)

# Load test dataset to find exact scenarios
test=pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\ml_dataset_test.csv", dtype={'pv_bus':str})
# Find the two false SAFE cases as identified: Bus 734 66kW and Bus 6231 53kW
# They are in test with label CONSTRAINED but predicted SAFE - find them
import pickle
model_data=pickle.load(open(r"C:\Users\ASUS\Documents\suryaghar\suryagrid_model.pkl","rb"))
model=model_data['model']
input_features=model_data['input_features']
X_test=test[input_features]
y_test=test['label']
pred=model.predict(X_test)
proba=model.predict_proba(X_test)
classes=list(model.classes_)  # alphabetical
print(f"Model classes: {classes}")
# Find indices where true CONSTRAINED and pred SAFE
for i in range(len(test)):
    if y_test.iloc[i]=="CONSTRAINED" and pred[i]=="SAFE":
        r=test.iloc[i]
        print(f"False SAFE {i}: bus {r['pv_bus']} exist {r['existing_pv_kw']} new {r['new_pv_kw']} total {r['total_pv_kw']} proba {proba[i]}")
# Specifically get the two mentioned
cases=[]
for bus,new in [("734",66),("6231",53)]:
    # find matching row(s) in test
    hit=test[(test['pv_bus']==bus) & (test['new_pv_kw']==new)]
    if len(hit)==0:
        print(f"No exact hit for {bus} {new}, searching pv_dataset.csv")
        pv=pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\pv_dataset.csv", dtype={'pv_bus':str})
        hit=pv[(pv['pv_bus']==bus) & (pv['new_pv_kw']==new)]
        print(hit.head().to_string())
        if len(hit)>0:
            cases.append(hit.iloc[0])
    else:
        print(f"Found {bus} {new} in ml_dataset_test:")
        print(hit[['pv_bus','existing_pv_kw','new_pv_kw','total_pv_kw','label','constraint_type','delta_pv_bus_voltage_pu','pv_max_voltage_pu','pv_max_transformer_loading_pct']].to_string())
        # also pull full pv_dataset row for details
        pv=pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\pv_dataset.csv", dtype={'pv_bus':str})
        full=pv[(pv['pv_bus']==bus) & (pv['new_pv_kw']==new) & (pv['existing_pv_kw']==int(hit.iloc[0]['existing_pv_kw']))]
        if len(full)>0:
            print("Full pv_dataset row:")
            print(full[['scenario_id','pv_bus','existing_pv_kw','new_pv_kw','total_pv_kw','label','constraint_type','constraint_reason','pv_max_voltage_pu','pv_max_transformer_loading_pct','worst_transformer','delta_pv_bus_voltage_pu']].to_string())
            cases.append(full.iloc[0])
        else:
            cases.append(hit.iloc[0])

# For diagnosis, use the exact existing/new from those rows
# If multiple, take first
template = pp.from_json(NET_PATH)

def diagnose_case(bus_id, existing_kw, new_kw, total_kw, scenario_id, expected_label):
# scenario_id may be missing for ml rows, generate fallback
    if scenario_id is None or (isinstance(scenario_id,float) and pd.isna(scenario_id)):
        scenario_id=f"{bus_id}_{new_kw}kW"
    print(f"\n{'='*80}")
    print(f"CASE {bus_id} scenario {scenario_id} existing {existing_kw} new {new_kw} total {total_kw} expected {expected_label}")
    print(f"{'='*80}")
    base_m,_,err = run_case(template, bus_id, existing_kw)
    if base_m is None:
        print(f"BASE failed {err}")
        return
    pv_m,_,err2 = run_case(template, bus_id, total_kw)
    if pv_m is None:
        print(f"PV failed {err2}")
        return
    base_vm = base_m["pv_bus_vm"]
    pv_vm = pv_m["pv_bus_vm"]
    delta = pv_vm - base_vm
    min_base = base_m["min_vm"]; max_base = base_m["max_vm"]
    min_pv = pv_m["min_vm"]; max_pv = pv_m["max_vm"]
    # Check violations
    def check(val, limit, comp=">"):
        if comp==">":
            return val > limit
        else:
            return val < limit
    # Build table rows
    rows=[]
    # Voltage high
    rows.append([bus_id, bus_id, f"{new_kw}kW", "PV bus voltage (pu)", f"{base_vm:.5f}", f"{pv_vm:.5f}", f"delta {delta:.5f}", "-", "-"])
    rows.append([bus_id, bus_id, "", "Feeder min voltage (pu)", f"{min_base:.5f} at {base_m['min_bus']}", f"{min_pv:.5f} at {pv_m['min_bus']}", f"{V_LOW_HARD:.2f} low hard", "YES" if min_pv < V_LOW_HARD else "NO"])
    rows.append([bus_id, bus_id, "", "Feeder max voltage (pu)", f"{max_base:.5f} at {base_m['max_bus']}", f"{max_pv:.5f} at {pv_m['max_bus']}", f"{V_HIGH_HARD:.2f} high hard", "YES" if max_pv > V_HIGH_HARD else "NO"])
    rows.append([bus_id, bus_id, "", "Voltage rise Δ at PV bus", "-", f"{delta:.5f}", f"{V_RISE_HARD:.2f} hard", "YES" if abs(delta) > V_RISE_HARD else "NO"])
    rows.append([bus_id, bus_id, "", "Max line loading (%)", f"{base_m['max_line']:.2f} {base_m['worst_line']}", f"{pv_m['max_line']:.2f} {pv_m['worst_line']}", f"{LINE_HARD:.0f}%", "YES" if pv_m['max_line']>LINE_HARD else "NO"])
    rows.append([bus_id, bus_id, "", "Max trafo loading (%)", f"{base_m['max_trafo']:.2f} {base_m['worst_trafo']}", f"{pv_m['max_trafo']:.2f} {pv_m['worst_trafo']}", f"{TRAFO_HARD:.0f}%", "YES" if pv_m['max_trafo']>TRAFO_HARD else "NO"])
    rows.append([bus_id, bus_id, "", "Source P (kW)", f"{base_m['ext_p']*1000:.1f}", f"{pv_m['ext_p']*1000:.1f}", "export <0", "YES" if pv_m['ext_p']<0 else "NO"])
    rows.append([bus_id, bus_id, "", "Source Q (kvar)", f"{base_m['ext_q']*1000:.1f}", f"{pv_m['ext_q']*1000:.1f}", "-", "-"])
    rows.append([bus_id, bus_id, "", "Losses (kW)", f"{base_m['losses_p']*1000:.1f}", f"{pv_m['losses_p']*1000:.1f}", "-", "-"])
    # Reverse
    rev=False
    rev_detail="none"
    if pv_m["ext_p"]<0:
        rev=True; rev_detail=f"source export {pv_m['ext_p']:.3f}MW"
    else:
        for lid,pb in base_m["line_p"].items():
            ppv=pv_m["line_p"].get(lid,0)
            if pb>0.01 and ppv<-0.01:
                rev=True; rev_detail=f"line {lid} {pb:.3f}->{ppv:.3f} reversed"; break
        if not rev:
            for tid,pb in base_m["trafo_p"].items():
                ppv=pv_m["trafo_p"].get(tid,0)
                if pb>0.01 and ppv<-0.01:
                    rev=True; rev_detail=f"trafo {tid} reversed"; break
    rows.append([bus_id, bus_id, "", "Reverse power flow", "0", "1" if rev else "0", "flag", rev_detail])
    # Print table
    print(f"{'Case':<6} {'Bus':<6} {'New PV':<8} {'Metric':<28} {'Before PV':<28} {'After PV':<28} {'Limit':<15} {'Viol?'}")
    print("-"*140)
    for r in rows:
        print(f"{r[0]:<6} {r[1]:<6} {r[2]:<8} {r[3]:<28} {r[4]:<28} {r[5]:<28} {r[6]:<15} {r[7]}")
    # Also print all trafo loadings sorted to identify
    print("\n--- All transformer loadings AFTER PV (sorted) ---")
    # need to map trafo idx to name
    # base_m and pv_m have res_trafo
    tmp = template  # not correct, need net
    # Instead use pv_m net
    # pv_m net is stored
    pv_net = pv_m["net"]
    # Actually pv_m is from run_case which includes net
    # Re-extract sorted
    # Get loadings
    loadings = []
    for idx in pv_net.trafo.index:
        name = pv_net.trafo.name.iloc[idx]
        ld = pv_net.res_trafo.loading_percent.iloc[idx]
        loadings.append((name, ld))
    loadings_sorted = sorted(loadings, key=lambda x: x[1], reverse=True)
    for name, ld in loadings_sorted[:10]:
        print(f"  {name:15s} {ld:.2f}%")
    # Also base loadings for compare
    print("\n--- Base transformer loadings (top 5) ---")
    base_net = base_m["net"]
    for name, ld in sorted([(base_net.trafo.name.iloc[i], base_net.res_trafo.loading_percent.iloc[i]) for i in base_net.trafo.index], key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {name:15s} {ld:.2f}%")
    # Line loadings
    print("\n--- PV line loadings top 5 ---")
    for name, ld in sorted([(pv_net.line.name.iloc[i], pv_net.res_line.loading_percent.iloc[i]) for i in pv_net.line.index], key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {name:35s} {ld:.2f}%")
    # Identify exact constraint per generation logic
    ctype="none"; creason="No violation"
    if pv_m["max_vm"]>V_HIGH_HARD:
        ctype="voltage"; creason=f"Max voltage {pv_m['max_vm']:.4f} at {pv_m['max_bus']} exceeds {V_HIGH_HARD}"
    elif pv_m["min_vm"]<V_LOW_HARD:
        ctype="voltage"; creason=f"Min {pv_m['min_vm']:.4f} below {V_LOW_HARD}"
    elif abs(delta)>V_RISE_HARD:
        ctype="voltage_rise"; creason=f"Rise {delta:.4f} exceeds {V_RISE_HARD}"
    elif pv_m["max_line"]>LINE_HARD:
        ctype="line_loading"; creason=f"Line {pv_m['worst_line']} {pv_m['max_line']:.1f}%"
    elif pv_m["max_trafo"]>TRAFO_HARD:
        ctype="transformer_loading"; creason=f"Trafo {pv_m['worst_trafo']} {pv_m['max_trafo']:.1f}%"
    else:
        # check caution
        pass
    print(f"\n>>> EXACT constraint per generation logic: {ctype} | {creason}")
    print(f">>> Dataset label: {expected_label}")
    # Also show dataset row values for comparison
    return base_m, pv_m, delta

# Find actual rows for diagnosis
# Use full pv_dataset for scenario_id, fallback to test
case_specs = []
for bus,new in [("734",66),("6231",53)]:
    hit=test[(test['pv_bus']==bus) & (test['new_pv_kw']==new)]
    if len(hit)==0:
        pv=pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\pv_dataset.csv", dtype={'pv_bus':str})
        hit=pv[(pv['pv_bus']==bus) & (pv['new_pv_kw']==new)]
    row=hit.iloc[0]
    # scenario_id may be in pv_dataset but not in ml_test; handle fallback
    sid = row['scenario_id'] if 'scenario_id' in row.index else f"{bus}_{new}kW"
    case_specs.append((bus, int(row['existing_pv_kw']), int(row['new_pv_kw']), int(row['total_pv_kw']), sid, row['label'], row))

for spec in case_specs:
    bus, exist, new, total, sid, label, row = spec
    base_m, pv_m, delta = diagnose_case(bus, exist, new, total, sid, label)
    # Also report BUS eligibility
    print("\n--- Eligibility check ---")
    import csv as csvm
    valid={}
    with open(VALID_BUSES_CSV,'r') as f:
        for r in csvm.DictReader(f):
            if r['bus_id']==bus:
                valid=r
                break
    if valid:
        print(f"Bus {bus} | PV eligible {valid['pv_eligible']} | Reason {valid['eligibility_reason']} | Section {valid['feeder_section']} | Trafo {valid['transformer_association']} | Load {valid['existing_load_kw']} kW | Base Vm {valid['base_voltage_pu']}")
    else:
        # check excluded
        import csv
        with open(r"C:\Users\ASUS\Documents\suryaghar\excluded_buses.csv",'r') as f:
            for r in csv.DictReader(f):
                if r['bus_id']==bus:
                    print(f"Bus {bus} EXCLUDED | {r['eligibility_reason']}")
                    break
    # ML info
    print("\n--- ML prediction for this case ---")
    ml_test=pd.read_csv(r"C:\Users\ASUS\Documents\suryaghar\ml_dataset_test.csv", dtype={'pv_bus':str})
    # find by bus and new, and existing if possible
    ml_row=ml_test[(ml_test['pv_bus']==bus) & (ml_test['new_pv_kw']==new) & (ml_test['existing_pv_kw']==exist)]
    if len(ml_row)==0:
        ml_row=ml_test[(ml_test['pv_bus']==bus) & (ml_test['new_pv_kw']==new)]
    if len(ml_row)>0:
        mr=ml_row.iloc[0]
        print(f"Input features:")
        for f in input_features:
            print(f"  {f}: {mr[f]}")
        proba = model.predict_proba(ml_row[input_features])
        pred = model.predict(ml_row[input_features])[0]
        print(f"ML prediction: {pred} (true {label})")
        print(f"Probabilities: {dict(zip(model.classes_, proba[0]))}")
        # dataset row already has constraint info
        # row is from pv_dataset which has full constraint_reason
        try:
            print(f"Constraint type in dataset: {row['constraint_type']} | {row['constraint_reason']}")
        except:
            print(f"Constraint type: {mr['constraint_type']}")
        try:
            print(f"Dataset pv_max_trafo {row['pv_max_transformer_loading_pct']}% worst {row['worst_transformer']}, pv_max_voltage {row['pv_max_voltage_pu']}")
        except:
            print(f"Dataset pv_max_trafo {mr['pv_max_transformer_loading_pct']}%")
    else:
        print("No ML row found")
