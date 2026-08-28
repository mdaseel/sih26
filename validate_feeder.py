"""
Validation: Compare pandapower balanced PF results with reference unbalanced report.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandapower as pp
import numpy as np
import math
import csv
import warnings
warnings.filterwarnings('ignore')

# Load network
net = pp.from_json(r'C:\Users\ASUS\Documents\suryaghar\feeder_network.json')
print(f"Loaded network: {len(net.bus)} buses, {len(net.line)} lines, {len(net.trafo)} trafos")

pp.runpp(net, algorithm='nr', calculate_voltage_angles=True,
         max_iteration=500, numba=False, tolerance_mva=1e-3,
         enforce_q_limits=False)
print("Power flow converged!\n")

# Build bus name -> index map
bd = {}
for idx in range(len(net.bus)):
    try:
        nm = int(net.bus.name.iloc[idx])
        bd[nm] = idx
    except:
        pass

# Parse reference TXT - find Phase A bus voltages
ref_file = r'C:\Users\ASUS\Documents\suryaghar\IEEE_CompTestFeeder_Results_20140401.txt'
with open(ref_file, 'r', encoding='utf-8', errors='replace') as f:
    ref_lines = f.readlines()

ref_bus_voltages = {}
i = 0
while i < len(ref_lines):
    line = ref_lines[i].strip()
    if not line:
        i += 1
        continue
    parts = line.split()
    if len(parts) < 6:
        i += 1
        continue
    # Check if first token is a bus number
    try:
        bus_num = int(parts[0])
    except:
        i += 1
        continue
    # Find Phase A line
    for p_offset in range(min(3, len(ref_lines) - i)):
        pline = ref_lines[i + p_offset].strip()
        pparts = pline.split()
        if len(pparts) < 6:
            continue
        # Find phase indicator
        has_phase_a = False
        for pp_val in pparts:
            if pp_val == 'A':
                has_phase_a = True
                break
        if not has_phase_a:
            continue
        # Find Pri kV (contains Y or D)
        pri_kv_str = ''
        base_v = 120.0
        for pp_idx, pp_val in enumerate(pparts):
            if ('Y' in pp_val or 'D' in pp_val) and not pri_kv_str:
                pri_kv_str = pp_val
                # Base voltage is the NEXT value after Pri kV
                if pp_idx + 1 < len(pparts):
                    try:
                        base_v = float(pparts[pp_idx + 1])
                    except:
                        pass
                break
        if pri_kv_str:
            ref_bus_voltages[bus_num] = {'pri_kv': pri_kv_str, 'base_v': base_v}
        break
    i += 3

# Compare bus voltages
print("=" * 80)
print("BUS VOLTAGE COMPARISON (Reference Phase A vs Balanced Positive-Sequence)")
print("=" * 80)
print(f"{'Bus':>6s} {'Ref_LN_kV':>10s} {'Ref_BaseV':>10s} {'Ref_pu':>8s} {'PP_pu':>8s} {'Error%':>8s}")

results = []
for bus_num in sorted(ref_bus_voltages.keys()):
    if bus_num not in bd:
        continue
    pp_idx = bd[bus_num]
    pp_vm = net.res_bus.vm_pu.iloc[pp_idx]
    pp_vn = net.bus.vn_kv.iloc[pp_idx]

    ref_a = ref_bus_voltages[bus_num]
    ref_pri_str = ref_a['pri_kv']
    ref_base_v = ref_a['base_v']

    ref_ln_kv = 0
    try:
        ref_ln_kv = float(ref_pri_str.replace('Y', '').replace('D', ''))
    except:
        pass

    ref_pu = ref_base_v / 120.0

    # For pandapower bus, convert L-L vn_kv to L-N for comparison
    pp_ln_kv = pp_vn / math.sqrt(3)

    err_pct = (pp_vm - ref_pu) / ref_pu * 100 if ref_pu > 0 else 0

    flag = ''
    if abs(err_pct) > 5: flag = '***'
    elif abs(err_pct) > 2: flag = '*'

    print(f"{bus_num:>6d} {ref_ln_kv:>10.2f} {ref_base_v:>10.1f} {ref_pu:>8.4f} {pp_vm:>8.4f} {err_pct:>+8.2f} {flag}")
    results.append({'bus': bus_num, 'ref_ln_kv': ref_ln_kv, 'ref_pu': ref_pu,
                    'pp_pu': pp_vm, 'pp_kv': pp_vn, 'err_pct': err_pct})

# Statistics
errors = [r['err_pct'] for r in results if r['ref_pu'] > 0]
if errors:
    print(f"\n--- Voltage Statistics ---")
    print(f"  MAE:  {np.mean(np.abs(errors)):.2f}%")
    print(f"  RMSE: {np.sqrt(np.mean(np.array(errors)**2)):.2f}%")
    print(f"  Max:  {np.max(np.abs(errors)):.2f}% (bus {results[np.argmax(np.abs(errors))]['bus']})")
    print(f"  Buses compared: {len(results)}")

# Source power
ext_p = net.res_ext_grid.p_mw.iloc[0]
ext_q = net.res_ext_grid.q_mvar.iloc[0]
print(f"\n--- Source Power ---")
print(f"  P = {ext_p:.4f} MW, Q = {ext_q:.4f} MVAR")

# Save
with open(r'C:\Users\ASUS\Documents\suryaghar\validation_results.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['Bus', 'Ref_LN_kV', 'Ref_BaseV', 'Ref_pu', 'PP_pu', 'PP_kV', 'Error_pct'])
    for r in results:
        w.writerow([r['bus'], r['ref_ln_kv'], r['ref_pu'], r['pp_pu'], r['pp_kv'], r['err_pct']])
print("\nResults saved to validation_results.csv")
