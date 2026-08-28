import pandapower as pp
from collections import defaultdict
import csv

net = pp.from_json(r'C:\Users\ASUS\Documents\suryaghar\feeder_network.json')
pp.runpp(net, algorithm='nr', max_iteration=500, numba=False, tolerance_mva=1e-3)

# Map pp bus idx -> name, vn
bus_info = {}
for idx,row in net.bus.iterrows():
    bus_info[idx] = {'name': str(row['name']), 'vn_kv': float(row['vn_kv']), 'vm_pu': float(net.res_bus.vm_pu.iloc[idx])}

# Aggregate load per bus (p_mw)
load_per_bus = defaultdict(float)
q_per_bus = defaultdict(float)
load_names = defaultdict(list)
for _,r in net.load.iterrows():
    load_per_bus[int(r['bus'])] += float(r['p_mw'])
    q_per_bus[int(r['bus'])] += float(r['q_mvar'])
    load_names[int(r['bus'])].append(str(r['name']))

# sgen per bus (subtract)
sgen_per_bus = defaultdict(float)
for _,r in net.sgen.iterrows():
    sgen_per_bus[int(r['bus'])] += float(r['p_mw'])

# Build transformer association: trafo lv_bus -> name
trafo_assoc = {}
for _,r in net.trafo.iterrows():
    lv = int(r['lv_bus'])
    hv = int(r['hv_bus'])
    trafo_assoc[lv] = str(r['name'])
    # also mark hv if needed
    if hv not in trafo_assoc:
        trafo_assoc[hv] = str(r['name'])+"(HV)"

# Feeder section via bus name prefix grouping
def feeder_section(name):
    try:
        n=int(name)
    except: return "secondary"
    if 620 <= n <= 633 or n>=6201: return "LV_secondary_T2_T4"
    if n in [708,710,712,714,715,716]: return "Branch_701-708"
    if n in [720,721,722,723,724,725,726,727,728,729,730,731,732,733,734]: return "Main_720-734"
    if n in [735,736,737,738,739,740,741,742,743,744,745,746,747,748,749,750]: return "Main_735-750"
    if n in [752,753,754,755,756,757,758,759,760,761,762,763,764,765]: return "Branch_752-765"
    if n in [766,767,768,769,770,771,772]: return "Delta_766-772"
    if n in [701,702,703,704,705,706,707,709,711,713,717,718,719]: return "Head_701-719"
    if n==700: return "Source"
    return "other"

# Determine eligibility
rows=[]
excluded=[]
total_buses = len(net.bus)

for idx,row in net.bus.iterrows():
    name = str(row['name'])
    vn = float(row['vn_kv'])
    vm = float(net.res_bus.vm_pu.iloc[idx]) if idx in bus_info else 0
    lp = load_per_bus.get(idx,0)
    lq = q_per_bus.get(idx,0)
    trafo = trafo_assoc.get(idx,"-")
    section = feeder_section(name)
    # Determine phase/config from vn and Excel mapping
    if vn==0.208:
        phase_cfg="Y - 120V L-N (0.208kV L-L)"
        vlevel="0.208 kV LV"
    elif vn==0.24:
        phase_cfg="Delta/CT 240V"
        vlevel="0.24 kV LV"
    elif vn==0.48:
        phase_cfg="3-phase 480V"
        vlevel="0.48 kV LV"
    elif vn==12.47:
        phase_cfg="Delta 12.47kV"
        vlevel="12.47 kV MV"
    elif vn==24.9:
        phase_cfg="Y 24.9kV primary"
        vlevel="24.9 kV MV"
    elif vn==34.5:
        phase_cfg="34.5kV"
        vlevel="34.5 kV MV"
    elif vn==115.0:
        phase_cfg="115kV source"
        vlevel="115 kV HV"
    else:
        phase_cfg="-"
        vlevel=f"{vn} kV"

    # Eligibility logic
    eligible=True
    reason=""
    if name=="700":
        eligible=False; reason="Source bus - not customer"
    elif vn>=12.47:
        # MV buses: exclude as rooftop is LV, but keep as ineligible with reason
        # Exception: we will mark MV as ineligible for Phase1 rooftop study
        eligible=False; reason="MV primary feeder - not LV rooftop (Phase1: LV only)"
    elif vn in [0.208,0.24,0.48]:
        # LV buses: check if isolated / no connectivity? All 114 are connected
        # Also exclude regulator internal? Regulators are MV, already excluded
        # Switch-only buses: check if bus has no load AND is secondary sub-bus with zero load but connected via switch - still valid (customer point)
        # For Phase1 we include all LV buses as eligible, even if load=0 (represents potential customer)
        eligible=True; reason="LV customer secondary - eligible"
        # Mark sub-buses explicitly
        if int(name) >=6201 or name in ["6201","6202","6211","6212","6221","6222","6231","6232","6241","6242","6251","6252","6261","6262","6321","6322","6331","6332","7121","7122","7391","7392","7393","7481","7482","7483","7641","7642","7643","7691","7692","7693"]:
            reason="LV secondary sub-bus (ideal switch to parent) - eligible"
    else:
        eligible=False; reason="Unknown voltage level"

    # Override: buses 715 is LV bridged to 714 but has no load - still eligible
    # Buses 721-726 etc have no load but are LV secondaries - keep eligible

    # Determine transformer association more precisely: find nearest upstream trafo
    # trafo variable already from lv_bus mapping, refine:
    assoc = trafo
    # improve: if bus is 620-626 etc, it is via T2 secondary 720 etc - mark T2
    if name in ["620","621","622","623","624","625","626","6201","6202","6211","6212","6221","6222","6231","6232","6241","6242","6251","6252","6261","6262"]:
        assoc="T2"
    if name in ["632","633","6321","6322","6331","6332"]:
        assoc="T4"
    if name in ["712","7121","7122"]:
        assoc="T18"
    if name in ["739","7391","7392","7393"]:
        assoc="T6"
    if name in ["748","7481","7482","7483"]:
        assoc="T8"
    if name in ["764","7641","7642","7643"]:
        assoc="T14"
    if name in ["769","7691","7692","7693"]:
        assoc="T22"

    rowd = {
        "bus_id": name,
        "bus_name": name,
        "pp_bus_idx": idx,
        "voltage_level_kv": vn,
        "voltage_level_label": vlevel,
        "phase_configuration": phase_cfg,
        "existing_load_kw": round(lp*1000,2),
        "existing_q_kvar": round(lq*1000,2),
        "base_voltage_pu": round(vm,4),
        "transformer_association": assoc,
        "feeder_section": section,
        "pv_eligible": "YES" if eligible else "NO",
        "eligibility_reason": reason
    }
    if eligible:
        rows.append(rowd)
    else:
        excluded.append(rowd)

# Write valid buses
import csv
fieldnames = ["bus_id","bus_name","pp_bus_idx","voltage_level_kv","voltage_level_label","phase_configuration","existing_load_kw","existing_q_kvar","base_voltage_pu","transformer_association","feeder_section","pv_eligible","eligibility_reason"]
with open(r'C:\Users\ASUS\Documents\suryaghar\valid_pv_buses.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for r in sorted(rows, key=lambda x: int(x['bus_id']) if x['bus_id'].isdigit() else 9999):
        w.writerow(r)

# Also write excluded for reporting
with open(r'C:\Users\ASUS\Documents\suryaghar\excluded_buses.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for r in sorted(excluded, key=lambda x: int(x['bus_id']) if str(x['bus_id']).isdigit() else 9999):
        w.writerow(r)

print(f"Total buses: {total_buses}")
print(f"Valid PV buses (LV): {len(rows)}")
print(f"Excluded buses: {len(excluded)}")
print("Valid list:", [r['bus_id'] for r in rows][:20], "...")
print("Excluded examples:", [(r['bus_id'], r['eligibility_reason']) for r in excluded[:10]])
# detailed breakdown
from collections import Counter
c=Counter([r['voltage_level_label'] for r in rows])
print("Valid voltage breakdown:", c)
c2=Counter([r['voltage_level_label'] for r in excluded])
print("Excluded voltage breakdown:", c2)
