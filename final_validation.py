"""Final Validation Script"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandapower as pp
import numpy as np
import math
import warnings
warnings.filterwarnings('ignore')

net = pp.from_json(r'C:\Users\ASUS\Documents\suryaghar\feeder_network.json')
pp.runpp(net, algorithm='nr', calculate_voltage_angles=True,
         max_iteration=500, numba=False, tolerance_mva=1e-3, enforce_q_limits=False)

bd = {}
for idx in range(len(net.bus)):
    try: bd[int(net.bus.name.iloc[idx])] = idx
    except: pass

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
    try:
        bus_num = int(parts[0])
    except:
        i += 1
        continue
    for p_offset in range(min(3, len(ref_lines) - i)):
        pline = ref_lines[i + p_offset].strip()
        pparts = pline.split()
        if len(pparts) < 6:
            continue
        has_phase_a = any(pp_val == 'A' for pp_val in pparts)
        if not has_phase_a:
            continue
        pri_kv_str = ''
        base_v = 120.0
        for pp_idx, pp_val in enumerate(pparts):
            if ('Y' in pp_val or 'D' in pp_val) and not pri_kv_str:
                pri_kv_str = pp_val
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

results = []
for bus_num in sorted(ref_bus_voltages.keys()):
    if bus_num not in bd:
        continue
    pp_idx = bd[bus_num]
    pp_vm = net.res_bus.vm_pu.iloc[pp_idx]
    ref_pu = ref_bus_voltages[bus_num]['base_v'] / 120.0
    err_pct = (pp_vm - ref_pu) / ref_pu * 100 if ref_pu > 0 else 0
    results.append({'bus': bus_num, 'ref_pu': ref_pu, 'pp_pu': pp_vm, 'err_pct': err_pct})

errors = [r['err_pct'] for r in results]
mae = np.mean(np.abs(errors))
rmse = np.sqrt(np.mean(np.array(errors)**2))
max_err_idx = int(np.argmax(np.abs(errors)))

print('=' * 60)
print('FINAL VALIDATION METRICS')
print('=' * 60)
print(f'Buses compared: {len(results)}')
print(f'MAE:  {mae:.2f}%')
print(f'RMSE: {rmse:.2f}%')
print(f'Max error: {np.max(np.abs(errors)):.2f}% (bus {results[max_err_idx]["bus"]})')
print()
print('10 WORST MISMATCHES:')
sorted_results = sorted(results, key=lambda r: abs(r['err_pct']), reverse=True)
for i, r in enumerate(sorted_results[:10]):
    print(f'  {i+1}. Bus {r["bus"]}: ref={r["ref_pu"]:.4f} pp={r["pp_pu"]:.4f} err={r["err_pct"]:+.2f}%')

print()
print('VOLTAGE PROFILE KEY BUSES:')
key_buses = [700, 701, 702, 704, 705, 706, 717, 718, 735, 736, 766, 767]
for b in key_buses:
    if b in bd:
        pp_vm = net.res_bus.vm_pu.iloc[bd[b]]
        ref_info = ref_bus_voltages.get(b, {})
        ref_pu = ref_info.get('base_v', 0) / 120.0
        err = (pp_vm - ref_pu) / ref_pu * 100 if ref_pu > 0 else 0
        print(f'  Bus {b}: ref={ref_pu:.4f} pp={pp_vm:.4f} err={err:+.2f}%')

ext_p = net.res_ext_grid.p_mw.iloc[0]
ext_q = net.res_ext_grid.q_mvar.iloc[0]
print(f'\nSource: P={ext_p:.4f} MW, Q={ext_q:.4f} MVAR')
print(f'Reference: P=4.139 MW, Q=1.316 MVAR')

print(f'\n{"="*60}')
print('TRANSFORMER LOADING:')
for idx in range(len(net.trafo)):
    name = net.trafo.name.iloc[idx]
    ld = net.res_trafo.loading_percent.iloc[idx]
    if not math.isnan(ld):
        flag = ' *** OVERLOAD' if ld > 100 else ''
        print(f'  {name:>12s}: {ld:6.1f}%{flag}')

print(f'\n{"="*60}')
print('BUSES OUT OF RANGE (ref > 1.0 pu):')
for r in sorted_results:
    if r['ref_pu'] >= 1.0 and r['err_pct'] < -3:
        print(f'  Bus {r["bus"]}: ref={r["ref_pu"]:.4f} pp={r["pp_pu"]:.4f} (gap={r["err_pct"]:+.2f}%)')
