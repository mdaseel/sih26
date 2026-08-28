import pandapower as pp, pandas as pd, networkx as nx, numpy as np, json, math
NET_PATH = r"C:\Users\ASUS\Documents\suryaghar\feeder_network.json"
VALID_CSV = r"C:\Users\ASUS\Documents\suryaghar\valid_pv_buses.csv"

net = pp.from_json(NET_PATH)
pp.runpp(net, algorithm='nr', numba=False)
# base voltages
base_vm = {str(net.bus.name.iloc[i]): float(net.res_bus.vm_pu.iloc[i]) for i in range(len(net.bus))}
# trafo rating map
trafo_rating = {str(row['name']): float(row['sn_mva'])*1000 for _,row in net.trafo.iterrows()}
# For buses with "-" or missing, map to upstream large trafo: use T-SUB 5000 for Main sections, else try to find nearest
# Also need line impedance cumulative

# Build graph with edge weights length and impedance
g = pp.topology.create_nxgraph(net)
# Need mapping from pp bus idx to name, and edge to line
# For distance and impedance, iterate over net.line
line_info = {}
for idx,row in net.line.iterrows():
    fb=int(row['from_bus']); tb=int(row['to_bus'])
    length=float(row['length_km'])
    # get std type r/x
    std=row['std_type']
    # std_types stored in net.std_types? Actually net.line has no r/x directly, need net.std_types?
    # Use net.line? net.line has r_ohm_per_km? Actually created via std_type, but line table has length and std_type name
    # Get r/x from net.std_types[std]
    # net.std_types is dict?
    try:
        r = net.std_types['line'][std]['r_ohm_per_km']
        x = net.std_types['line'][std]['x_ohm_per_km']
    except:
        r=0.5; x=0.5
    # store bidirectional
    line_info[(fb,tb)] = (length, r*length, x*length)
    line_info[(tb,fb)] = (length, r*length, x*length)

def idx_for(name):
    hits = net.bus.index[net.bus.name==str(name)]
    return int(hits[0]) if len(hits)>0 else None

# Compute for each valid bus
valid=pd.read_csv(VALID_CSV, dtype={'bus_id':str})
src_idx = idx_for('700')
results=[]
for _,row in valid.iterrows():
    bus_id=str(row['bus_id'])
    bus_idx=idx_for(bus_id)
    if bus_idx is None:
        print(f"skip {bus_id} not in net")
        continue
    # transformer_sn
    assoc = str(row['transformer_association'])
    if assoc in trafo_rating:
        sn = trafo_rating[assoc]
    elif assoc=="-":
        # For Main sections without dedicated trafo, use T-SUB as upstream
        sn = trafo_rating.get("T-SUB",5000)
        # For LV_secondary_T2_T4 with "-" shouldn't happen, but fallback
    elif assoc not in trafo_rating and assoc.startswith("T"):
        # try find closest
        sn = 300 # default 300kVA
    else:
        sn = 300
    # base voltage
    base_v = base_vm.get(bus_id, 1.0)
    # distance and impedance via shortest path
    try:
        path = nx.shortest_path(g, src_idx, bus_idx)
        dist=0; r_tot=0; x_tot=0
        for i in range(len(path)-1):
            a=path[i]; b=path[i+1]
            # find edge line
            if (a,b) in line_info:
                l,r,x = line_info[(a,b)]
                dist+=l; r_tot+=r; x_tot+=x
            else:
                # may be trafo or switch edge (zero length) - check trafo
                # find trafo connecting a-b
                trafo_edge = net.trafo[(net.trafo.hv_bus==a) & (net.trafo.lv_bus==b) | (net.trafo.hv_bus==b) & (net.trafo.lv_bus==a)]
                if len(trafo_edge)>0:
                    # trafo impedance not counted for distance, but for electrical distance we use 0
                    pass
                else:
                    # switch ideal 0
                    pass
        z_mag = math.sqrt(r_tot**2 + x_tot**2)
    except Exception as e:
        dist=np.nan; r_tot=np.nan; x_tot=np.nan; z_mag=np.nan
        print(f"path fail for {bus_id}: {e}")
    results.append({"bus_id":bus_id, "transformer_sn_kva":sn, "base_voltage_pu":round(base_v,5), "feeder_distance_km":round(dist,4) if not np.isnan(dist) else np.nan, "upstream_r_ohm":round(r_tot,4), "upstream_x_ohm":round(x_tot,4), "upstream_z_ohm":round(z_mag,4)})

df=pd.DataFrame(results)
print(df.head(20).to_string())
print(df.describe().to_string())
# Save for join
df.to_csv(r"C:\Users\ASUS\Documents\suryaghar\electrical_features.csv", index=False)
print("Saved electrical_features.csv")

# Show examples for false cases
for b in ['734','6231','708','720']:
    print(df[df.bus_id==b].to_string())
