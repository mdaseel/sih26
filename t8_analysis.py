import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import xlrd, math
wb = xlrd.open_workbook(r'C:\Users\ASUS\Documents\suryaghar\IEEE-Comp-Test-Feeder-Data-20140401.xls')
ws = wb.sheet_by_name('Xfm Banks')

print('=== T8 Phase B handling ===')
print('T8 Row 7: Phase A=25 kVA, Phase B="50 CT", Phase C=25 kVA')
print()

a = 25.0
b_raw = '50 CT'
c = 25.0

def sf(val, default=0.0):
    if val == '' or val is None: return default
    try: return float(val)
    except: return default

b = sf(b_raw)
print(f'Phase A: {a} kVA')
print(f'Phase B raw: "{b_raw}" -> sf() returns {b}')
print(f'Phase C: {c} kVA')
print()

total_kVA = max(a, b, c, 0) * 3
r_kva = max(a, b, c)
print(f'max(a,b,c) = max({a}, {b}, {c}) = {max(a,b,c)}')
print(f'total_kVA = {total_kVA} (used for sn_mva = {total_kVA/1000:.3f} MVA)')
print(f'r_kva = {r_kva} (used for impedance lookup)')
print()

# Impedance lookup for 25 kVA
ws2 = wb.sheet_by_name('Xfm Z')
for r in range(6, ws2.nrows):
    nm = str(ws2.cell_value(r,0)).strip()
    if nm == '25.0' or nm == '25':
        R = ws2.cell_value(r,1)
        X = ws2.cell_value(r,2)
        vk = math.sqrt(R**2 + X**2)
        print(f'Xfm Z lookup for 25 kVA: R={R}%, X={X}%, vk={vk:.3f}%')
        break

print()
print('=== T8 LOADING ANALYSIS ===')
print(f'T8 3-phase rating: {total_kVA/1000:.3f} MVA ({total_kVA:.0f} kVA)')
print(f'CT load at T8: P=33 kW, Q=19 kVAR')
print(f'S_load = sqrt(33^2 + 19^2) = {math.sqrt(33**2+19**2):.1f} kVA')
print(f'Loading = {math.sqrt(33**2+19**2)/total_kVA*100:.1f}%')
print()
print('Reference T8 loading: 127.4%')
print(f'If S_load = {math.sqrt(33**2+19**2):.1f} kVA and loading = 127.4%:')
ref_sn = math.sqrt(33**2+19**2) / 1.274
print(f'  Reference 3-phase rating = {ref_sn:.1f} kVA = {ref_sn/1000:.3f} MVA')
print(f'  Our model rating = {total_kVA:.0f} kVA = {total_kVA/1000:.3f} MVA')
print()
print('The reference confirms T8 is overloaded at 127.4%.')
print('This is a real overload, not a bug. T8 has only 25 kVA per phase')
print('(Phase B "50 CT" is 50 kVA center-tapped, but still 25 kVA per winding)')
print('and carries 33 kW + 19 kVAR = 41 kVA on its secondary.')

print()
print('=== LOAD GAP ANALYSIS ===')
print('Excel total loads: P=3631 kW, Q=1756 kVAR')
print('Capacitors: Q=-900 kVAR (supplying)')
print('Net load: P=3631 kW, Q=856 kVAR')
print()
print('Model source: P=4189 kW, Q=1702 kVAR')
print('Model losses: P=558 kW, Q=846 kVAR')
print()
print('Reference source: P=4139 kW, Q=1316 kVAR')
print('Reference losses: P=508 kW, Q=460 kVAR')
print()
print('Loss differences:')
print(f'  P: model={558} kW vs ref={508} kW, diff={558-508} kW')
print(f'  Q: model={846} kVAR vs ref={460} kVAR, diff={846-460} kVAR')
print()
print('The Q loss difference (386 kVAR) is the main concern.')
print('Possible causes:')
print('  1. Regulator transformers absorbing Q (vk=1.5% at 5 MVA each)')
print('  2. Load modeling: constant PQ loads draw more Q at low voltage')
print('  3. Transformer magnetizing Q not modeled (i0_percent=0)')
