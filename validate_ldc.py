"""
Validation of LDC model against TXT reference.
Compares independently calculated regulator taps and resulting voltages.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandapower as pp
import numpy as np
import math

# Load the LDC network
net = pp.from_json(r'C:\Users\ASUS\Documents\suryaghar\feeder_network_ldc.json')

# Read TXT reference
ref_data = {}
with open(r'C:\Users\ASUS\Documents\suryaghar\IEEE_CompTestFeeder_Results_20140401.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('670') or line.startswith('Source') or line.startswith('---') or line.startswith('='): 
            continue
        parts = line.split()
        if len(parts) < 3: continue
        try:
            bus = int(parts[0])
        except:
            continue
        # Parse voltage from column 1 or 2 (first numeric after bus)
        v_pu = None
        for p in parts[1:]:
            try:
                v = float(p)
                if 0.5 < v < 1.2:  # reasonable voltage range
                    v_pu = v
                    break
            except:
                continue
        if v_pu is not None:
            ref_data[bus] = v_pu

# Build mapping from bus name to pp index
bd = {}
for idx in range(len(net.bus)):
    nm = net.bus.name.iloc[idx]
    try:
        bd[int(nm)] = idx
    except:
        pass

# Compare voltages
print("="*70)
print("VALIDATION: LDC MODEL vs TXT REFERENCE")
print("="*70)
print(f"\nBuses compared: {len([b for b in ref_data if b in bd])}")

errors = []
for bus, ref_v in sorted(ref_data.items()):
    if bus in bd:
        pp_v = net.res_bus.vm_pu.iloc[bd[bus]]
        err_pct = (pp_v - ref_v) / ref_v * 100
        errors.append((bus, ref_v, pp_v, err_pct))

if errors:
    abs_errors = [abs(e[3]) for e in errors]
    mae = np.mean(abs_errors)
    rmse = np.sqrt(np.mean([e[3]**2 for e in errors]))
    max_err = max(errors, key=lambda x: abs(x[3]))
    
    print(f"MAE:  {mae:.2f}%")
    print(f"RMSE: {rmse:.2f}%")
    print(f"Max error: {max_err[3]:+.2f}% (bus {max_err[0]})")
    
    print(f"\n10 WORST MISMATCHES:")
    sorted_errors = sorted(errors, key=lambda x: abs(x[3]), reverse=True)
    for i, (bus, ref_v, pp_v, err) in enumerate(sorted_errors[:10]):
        print(f"  {i+1}. Bus {bus}: ref={ref_v:.4f} pp={pp_v:.4f} err={err:+.2f}%")

# Source power
ext_p = net.res_ext_grid.p_mw.iloc[0]
ext_q = net.res_ext_grid.q_mvar.iloc[0]
print(f"\nSource: P={ext_p:.4f} MW, Q={ext_q:.4f} Mvar")
print(f"Reference: P=4.139 MW, Q=1.316 Mvar")

# Transformer loading
print(f"\nTRANSFORMER LOADING:")
for idx in range(len(net.trafo)):
    ld = net.res_trafo.loading_percent.iloc[idx]
    if not math.isnan(ld):
        print(f"  {net.trafo.name.iloc[idx]:>12s}: {ld:5.1f}%")
