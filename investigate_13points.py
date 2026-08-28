"""
IEEE Comp Test Feeder - Comprehensive 13-Point Investigation
Traces every parameter from Excel through to the model results.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandapower as pp
import numpy as np
import xlrd
import math
import warnings
warnings.filterwarnings('ignore')

xls_path = r"C:\Users\ASUS\Documents\suryaghar\IEEE-Comp-Test-Feeder-Data-20140401.xls"
wb = xlrd.open_workbook(xls_path)

def sf(val, default=0.0):
    if val == '' or val is None: return default
    try: return float(val)
    except: return default
def si(val, default=0):
    if val == '' or val is None: return default
    try: return int(val)
    except: return default

def sym_seq_Z(z_abc):
    a = np.exp(1j * 2 * np.pi / 3)
    A = np.array([[1,1,1],[1,a**2,a],[1,a,a**2]])
    return np.linalg.inv(A) @ z_abc @ A

# ============================================================
# 1. T-SUB INVESTIGATION
# ============================================================
print("="*60)
print("1. T-SUB INVESTIGATION")
print("="*60)

ws = wb.sheet_by_name('Sub Xfm')
print("\nRaw Excel data:")
for c in range(10):
    print(f"  Col {c}: {ws.cell_value(2,c)}")
for c in range(10):
    print(f"  Col {c}: {ws.cell_value(3,c)}")

sub_R = sf(ws.cell_value(3,5))
sub_X = sf(ws.cell_value(3,6))
sub_kVA = sf(ws.cell_value(3,4))
sub_Z = math.sqrt(sub_R**2 + sub_X**2)

print(f"\nExcel values: R={sub_R}%, X={sub_X}%, kVA={sub_kVA}")
print(f"Computed: Z = sqrt(R²+X²) = sqrt({sub_R}²+{sub_X}²) = {sub_Z:.3f}%")
print(f"X/R ratio = {sub_X/sub_R:.1f}")

# pandapower parameters
print(f"\npandapower parameters:")
print(f"  sn_mva = {sub_kVA/1000:.3f}")
print(f"  vn_hv_kv = 115.0")
print(f"  vn_lv_kv = 24.9")
print(f"  vkr_percent = {sub_R}")
print(f"  vk_percent = {sub_Z:.3f}")

# Expected voltage drop at reference loading
# Reference: 77% loading, P=1242 kW, Q=418 kVAR per phase
ref_loading = 0.77
ref_P_ph = 1242  # kW per phase
ref_Q_ph = 418   # kVAR per phase
ref_S_ph = math.sqrt(ref_P_ph**2 + ref_Q_ph**2)
ref_S_total = ref_S_ph * 3

print(f"\nReference loading: {ref_loading*100:.0f}%")
print(f"  P per phase: {ref_P_ph} kW, Q per phase: {ref_Q_ph} kVAR")
print(f"  S per phase: {ref_S_ph:.0f} kVA, S total: {ref_S_total:.0f} kVA")
print(f"  S rated: {sub_kVA} kVA")

# Voltage drop formula: delta_V% = (R%*P_ph + X%*Q_ph) / (S_rated/3)
delta_V_ref = (sub_R * ref_P_ph + sub_X * ref_Q_ph) / (sub_kVA/3)
print(f"\n  Voltage drop (per phase):")
print(f"    delta_V = (R%*P + X%*Q) / S_rated_ph")
print(f"    = ({sub_R}*{ref_P_ph} + {sub_X}*{ref_Q_ph}) / ({sub_kVA}/3)")
print(f"    = ({sub_R*ref_P_ph:.1f} + {sub_X*ref_Q_ph:.1f}) / {sub_kVA/3:.1f}")
print(f"    = {delta_V_ref:.2f}%")
print(f"    On 120V base: {delta_V_ref*120/100:.3f}V")

# Reference shows 0.47V element drop
print(f"\n  Reference element drop: 0.47V = 0.39%")
print(f"  Our calculated drop: {delta_V_ref:.2f}%")
print(f"  Ratio: {delta_V_ref/0.39:.2f}x")

# If Z were on a different base...
print(f"\n  What Z would give 0.39% drop?")
needed = 0.39 * (sub_kVA/3) / (sub_R/sub_X * ref_P_ph + ref_Q_ph)
print(f"  If X/R ratio maintained: X_needed = {needed:.3f}%")

# Direct calculation: what Z gives 0.39%?
# 0.39 = (R*1242 + X*418) / (5000/3)
# 0.39 * 1666.7 = R*1242 + X*418
# With X/R = 8: 653.3 = R*1242 + 8R*418 = R*(1242+3344) = R*4586
R_needed = 0.39 * (sub_kVA/3) / (ref_P_ph + (sub_X/sub_R)*ref_Q_ph)
X_needed = (sub_X/sub_R) * R_needed
print(f"  R_needed = {R_needed:.4f}%, X_needed = {X_needed:.4f}%")
print(f"  This is {R_needed/sub_R*100:.1f}% of Excel R and {X_needed/sub_X*100:.1f}% of Excel X")

# ============================================================
# 2. SOURCE Q DISCREPANCY - Element by Element
# ============================================================
print("\n" + "="*60)
print("2. SOURCE Q DISCREPANCY - Element-by-Element Trace")
print("="*60)

# Read all load data
ws = wb.sheet_by_name('Loads')
print("\n--- Distributed Loads ---")
total_dist_P = 0; total_dist_Q = 0
for r in [3,4,5,6,7,8,9]:
    nm = ws.cell_value(r,0)
    if not nm or nm=='': continue
    model = ws.cell_value(r,3)
    ka = sf(ws.cell_value(r,4)); qa = sf(ws.cell_value(r,5))
    kb = sf(ws.cell_value(r,6)); qb = sf(ws.cell_value(r,7))
    kc = sf(ws.cell_value(r,8)); qc = sf(ws.cell_value(r,9))
    tw = ka+kb+kc; tq = qa+qb+qc
    total_dist_P += tw; total_dist_Q += tq
    print(f"  {nm}: model={model}, P={tw:.1f} kW, Q={tq:.1f} kVAR, PF={tw/math.sqrt(tw**2+tq**2)*100:.1f}%" if tw>0 or tq>0 else f"  {nm}: empty")

print(f"\n  Total distributed: P={total_dist_P:.1f} kW, Q={total_dist_Q:.1f} kVAR")

print("\n--- Transformer Loads ---")
total_xfm_P = 0; total_xfm_Q = 0
for r in range(14,28):
    nm = ws.cell_value(r,0)
    if not nm or nm=='': continue
    model = ws.cell_value(r,3)
    ka = sf(ws.cell_value(r,4)); qa = sf(ws.cell_value(r,5))
    kb = sf(ws.cell_value(r,6)); qb = sf(ws.cell_value(r,7))
    kc = sf(ws.cell_value(r,8)); qc = sf(ws.cell_value(r,9))
    tw = ka+kb+kc; tq = qa+qb+qc
    total_xfm_P += tw; total_xfm_Q += tq
    if tw>0 or tq>0:
        print(f"  {nm}: model={model}, P={tw:.1f} kW, Q={tq:.1f} kVAR, PF={tw/math.sqrt(tw**2+tq**2)*100:.1f}%")

print(f"\n  Total transformer loads: P={total_xfm_P:.1f} kW, Q={total_xfm_Q:.1f} kVAR")

print("\n--- CT Loads ---")
total_ct_P = 0; total_ct_Q = 0
for r in range(32,51):
    nm = ws.cell_value(r,0)
    if not nm or nm=='': continue
    model = ws.cell_value(r,3)
    k1a = sf(ws.cell_value(r,4)); q1a = sf(ws.cell_value(r,5))
    k1b = sf(ws.cell_value(r,6)); q1b = sf(ws.cell_value(r,7))
    k24 = sf(ws.cell_value(r,8)); q24 = sf(ws.cell_value(r,9))
    tp = k1a+k1b+k24; tq = q1a+q1b+q24
    total_ct_P += tp; total_ct_Q += tq
    if tp>0 or tq>0:
        print(f"  {nm}: model={model}, P={tp:.1f} kW, Q={tq:.1f} kVAR")

print(f"\n  Total CT loads: P={total_ct_P:.1f} kW, Q={total_ct_Q:.1f} kVAR")

# Machines
ws = wb.sheet_by_name('Machines')
print("\n--- Machines ---")
total_mach_P = 0; total_mach_Q = 0
for r in range(2, ws.nrows):
    nm = ws.cell_value(r,0)
    if not nm: continue
    hp = sf(ws.cell_value(r,2))
    V = sf(ws.cell_value(r,3))
    spec = str(ws.cell_value(r,9) or '')
    sp = spec.lower()

    if 'gen' in nm.lower():
        if 'kw out' in sp:
            kw = float(sp.split('=')[1].strip().split()[0])
        else:
            kw = hp*0.746*0.85
        q = kw * 0.48  # model estimate
        pf_ref = 0.90  # assumed
        total_mach_P -= kw  # generator
        total_mach_Q -= q
        print(f"  {nm} (GEN): spec='{spec}', P_out={kw:.1f} kW, model_Q={q:.1f} kVAR")
    elif 'motor' in nm.lower():
        if 'kw input' in sp:
            kw = float(sp.split('=')[1].strip().split()[0])
            pf = 0.85
        elif 'pf' in sp:
            pf_str = sp.split('pf')[1].split('%')[0].split('=')[1].strip()
            pf = float(pf_str) / 100.0
            kw = hp*0.746/0.85
        else:
            kw = hp*0.746*0.85
            pf = 0.82
        q = kw * math.tan(math.acos(pf))
        total_mach_P += kw
        total_mach_Q += q
        print(f"  {nm} (MOTOR): spec='{spec}', P={kw:.1f} kW, PF={pf*100:.1f}%, Q={q:.1f} kVAR")

print(f"\n  Total machines: P={total_mach_P:.1f} kW, Q={total_mach_Q:.1f} kVAR")

# Capacitors
ws = wb.sheet_by_name('Capacitors')
print("\n--- Capacitors ---")
total_cap_Q = 0
for r in range(3, ws.nrows):
    nm = ws.cell_value(r,0)
    if not nm: continue
    sw = ws.cell_value(r,6)
    a = sf(ws.cell_value(r,3)); b = sf(ws.cell_value(r,4)); c = sf(ws.cell_value(r,5))
    tq = a+b+c
    if str(sw).lower()=='closed':
        total_cap_Q -= tq
        print(f"  {nm}: closed, Q=-{tq:.1f} kVAR (supplying)")
    else:
        print(f"  {nm}: open, Q={tq:.1f} kVAR (not connected)")

print(f"\n  Total capacitor Q: {total_cap_Q:.1f} kVAR")

# Summary
total_P = total_dist_P + total_xfm_P + total_ct_P + total_mach_P
total_Q = total_dist_Q + total_xfm_Q + total_ct_Q + total_mach_Q + total_cap_Q
print(f"\n--- TOTAL LOAD SUMMARY ---")
print(f"  P_total = {total_P:.1f} kW = {total_P/1000:.3f} MW")
print(f"  Q_total = {total_Q:.1f} kVAR = {total_Q/1000:.3f} MVAR")
print(f"  S_total = {math.sqrt(total_P**2+total_Q**2):.1f} kVA")
print(f"  PF = {total_P/math.sqrt(total_P**2+total_Q**2)*100:.1f}%")

# Reference source
print(f"\n  Reference source: P=4139 kW, Q=1316 kVAR")
print(f"  Our total load:   P={total_P:.0f} kW, Q={total_Q:.0f} kVAR")
print(f"  Difference:       P={total_P-4139:+.0f} kW, Q={total_Q-1316:+.0f} kVAR")

# ============================================================
# 3. LOAD MODELING
# ============================================================
print("\n" + "="*60)
print("3. LOAD MODELING")
print("="*60)

ws = wb.sheet_by_name('Loads')
print("\nLoad types in Excel:")
load_types = {}
for r in list(range(3,10)) + list(range(14,28)) + list(range(32,51)):
    nm = ws.cell_value(r,0)
    if not nm or nm=='': continue
    model = ws.cell_value(r,3)
    if model and model != '':
        if model not in load_types: load_types[model] = 0
        load_types[model] += 1
        print(f"  Row {r}: {nm}: model={model}")

print(f"\nSummary of load types:")
for mt, count in sorted(load_types.items()):
    print(f"  {mt}: {count} loads")

print(f"\nAll loads currently modeled as constant PQ.")
print(f"Types Y-I, Y-Z, D-I, D-Z, CT-I, CT-Z should be constant-I or constant-Z.")
print(f"pandapower supports const_z_p_mw and const_i_p_mw in create_load.")

# ============================================================
# 4. MOTOR MODEL
# ============================================================
print("\n" + "="*60)
print("4. MOTOR MODEL VERIFICATION")
print("="*60)

ws = wb.sheet_by_name('Machines')
print(f"\n{'Name':<12} {'Node':>6} {'HP':>6} {'V':>6} {'Spec':<30} {'P(kW)':>8} {'PF%':>6} {'Q(kVAR)':>8} {'Model Element':<10}")
print("-"*100)
for r in range(2, ws.nrows):
    nm = ws.cell_value(r,0)
    if not nm: continue
    hp = sf(ws.cell_value(r,2))
    V = sf(ws.cell_value(r,3))
    node = si(ws.cell_value(r,1))
    spec = str(ws.cell_value(r,9) or '')
    sp = spec.lower()

    if 'gen' in nm.lower():
        if 'kw out' in sp:
            kw = float(sp.split('=')[1].strip().split()[0])
        else:
            kw = hp*0.746*0.85
        q = kw * 0.48
        pf_model = kw/math.sqrt(kw**2+q**2)*100
        print(f"{nm:<12} {node:>6} {hp:>6.0f} {V:>6.0f} {spec:<30} {kw:>8.1f} {pf_model:>6.1f} {q:>8.1f} sgen")
    elif 'motor' in nm.lower():
        if 'kw input' in sp:
            kw = float(sp.split('=')[1].strip().split()[0])
            pf = 0.85
        elif 'pf' in sp:
            pf_str = sp.split('pf')[1].split('%')[0].split('=')[1].strip()
            pf = float(pf_str) / 100.0
            kw = hp*0.746/0.85
        else:
            kw = hp*0.746*0.85
            pf = 0.82
        q = kw * math.tan(math.acos(pf))
        print(f"{nm:<12} {node:>6} {hp:>6.0f} {V:>6.0f} {spec:<30} {kw:>8.1f} {pf*100:>6.1f} {q:>8.1f} load")

print(f"\nReference motor data:")
print(f"  Motor 1 (716): ref P=20 kW, Q=14 kVAR, PF=82%")
print(f"  Motor 2 (762): ref P=29 kW, Q=16 kVAR, PF=86%")
print(f"  Motor 3 (748): ref P=19 kW, Q=12 kVAR, PF=85%")
print(f"  Motor 4 (734): ref P=9 kW, Q=6 kVAR, PF=83%")

# ============================================================
# 5. GENERATORS
# ============================================================
print("\n" + "="*60)
print("5. GENERATORS")
print("="*60)

ws = wb.sheet_by_name('Machines')
for r in range(2, ws.nrows):
    nm = ws.cell_value(r,0)
    if not nm: continue
    spec = str(ws.cell_value(r,9) or '')
    sp = spec.lower()
    if 'gen' in nm.lower():
        hp = sf(ws.cell_value(r,2))
        if 'kw out' in sp:
            kw = float(sp.split('=')[1].strip().split()[0])
        else:
            kw = hp*0.746*0.85
        q_model = kw * 0.48
        q_ref = 89.0  # from TXT reference
        print(f"  {nm}:")
        print(f"    Excel: hp={hp}, spec='{spec}'")
        print(f"    Extracted: kW_out={kw}")
        print(f"    Model Q: {q_model:.1f} kVAR (using pf~90%)")
        print(f"    Reference Q: {q_ref} kVAR")
        print(f"    Mismatch: {q_model - q_ref:+.1f} kVAR")
        print(f"    Reference shows Q>0 meaning generator absorbs VARs (induction gen)")

# ============================================================
# 6. REGULATORS
# ============================================================
print("\n" + "="*60)
print("6. REGULATORS")
print("="*60)

ws = wb.sheet_by_name('Regulators')
print(f"\n{'Name':<8} {'From':>5} {'To':>5} {'Conn':<10} {'Phases':<8} {'PT':>5} {'CT':>5} {'SetV':>5} {'CompR':>6} {'CompX':>6} {'Mode':<12}")
print("-"*85)
for r in [6,7,8,9,12]:
    nm = ws.cell_value(r,0)
    if not nm or nm=='': continue
    fr = si(ws.cell_value(r,1)); tv = si(ws.cell_value(r,2))
    conn = ws.cell_value(r,3); phases = ws.cell_value(r,5)
    pt = sf(ws.cell_value(r,6)); ct = sf(ws.cell_value(r,7))
    sv = sf(ws.cell_value(r,8)); cr = sf(ws.cell_value(r,9))
    cx = sf(ws.cell_value(r,10)); mode = ws.cell_value(r,11)
    print(f"{nm:<8} {fr:>5} {tv:>5} {conn:<10} {phases:<8} {pt:>5.0f} {ct:>5.0f} {sv:>5.0f} {cr:>6.1f} {cx:>6.1f} {mode}")

print(f"\nRegulator step info:")
print(f"  32 steps, ±10%, step size = 5/8% = 0.625%")
print(f"  Bandwidth = 2V")
print(f"  Ratio = 1 + tap * 0.00625")

print(f"\nCurrent model: hard-coded tap positions from reference TXT.")
print(f"  Reg 1: tap=7.7, ratio=1.0481")
print(f"  Reg 2: tap=12.7, ratio=1.0794")
print(f"  Reg 3: tap=5.1, ratio=1.0319")
print(f"  Reg 4: tap=3.0, ratio=1.0188")
print(f"  Reg 5: tap=-5.8, ratio=0.9637")

print(f"\nLimitation: Full LDC control requires:")
print(f"  1. Measure V at load side through PT")
print(f"  2. Measure I through CT")
print(f"  3. Compute V_comp = V + I*(CompR + j*CompX)")
print(f"  4. Compare V_comp with SetV")
print(f"  5. Adjust tap to make V_comp = SetV")
print(f"This requires unbalanced 3-phase model or iterative tap adjustment.")

# ============================================================
# 7. T8 TRANSFORMER
# ============================================================
print("\n" + "="*60)
print("7. T8 TRANSFORMER INVESTIGATION")
print("="*60)

ws = wb.sheet_by_name('Xfm Banks')
print("\nT8 in Excel:")
for r in range(3, ws.nrows):
    nm = ws.cell_value(r,0)
    if nm and 'T8' in str(nm):
        row = [ws.cell_value(r,c) for c in range(9)]
        print(f"  Row {r}: {row}")

ws = wb.sheet_by_name('Xfm Z')
print("\nImpedance lookup for T8:")
print(f"  T8 is a single-phase bank (3 single-phase units)")
print(f"  Per-phase kVA determines impedance lookup")

# T8 data from Excel
print(f"\n  T8 connection: Secondary side: 748 -> 7481/7482/7483")
print(f"  Load at 748: CT loads from T8")

ws = wb.sheet_by_name('Loads')
print(f"\n  Loads at T8 (node 748/748x):")
for r in range(32,51):
    nm = ws.cell_value(r,0)
    if not nm or nm=='': continue
    node = si(ws.cell_value(r,1))
    if node in [748, 7481, 7482, 7483]:
        k1a = sf(ws.cell_value(r,4)); q1a = sf(ws.cell_value(r,5))
        k1b = sf(ws.cell_value(r,6)); q1b = sf(ws.cell_value(r,7))
        k24 = sf(ws.cell_value(r,8)); q24 = sf(ws.cell_value(r,9))
        tp = k1a+k1b+k24; tq = q1a+q1b+q24
        print(f"    {nm} @ node {node}: P={tp:.1f} kW, Q={tq:.1f} kVAR")

# ============================================================
# 8. LINE IMPEDANCE
# ============================================================
print("\n" + "="*60)
print("8. LINE IMPEDANCE AUDIT")
print("="*60)

ws = wb.sheet_by_name('Config Z&Y')
print("\nFirst few configurations and their positive-sequence Z:")
cfg_count = 0
r = 4
while r < ws.nrows and cfg_count < 5:
    cv = ws.cell_value(r, 0)
    if cv == '' or cv is None: r += 1; continue
    if isinstance(cv, str) and ('self' in cv or 'mutual' in cv):
        r += 4; continue
    cn = sf(cv)
    if cn == 0: r += 1; continue
    zb = np.zeros((3,3), dtype=complex)
    for i in range(3):
        ri = r+i
        if ri >= ws.nrows: break
        v = [sf(ws.cell_value(ri,c)) for c in range(1,min(11,ws.ncols))]
        while len(v)<10: v.append(0)
        zb[i] = [complex(v[0],v[1]),complex(v[2],v[3]),complex(v[4],v[5])]
    Z012 = sym_seq_Z(zb)
    Z1 = Z012[1,1]
    r_km = Z1.real / 1.60934
    x_km = Z1.imag / 1.60934
    print(f"  Config {int(cn)}: Z1 = {Z1:.4f} ohm/mile = ({r_km:.4f} + j{x_km:.4f}) ohm/km")
    cfg_count += 1
    r += 4

print("\nLines with their configurations:")
ws = wb.sheet_by_name('Lines')
for r in range(2, min(10, ws.nrows)):
    nm = ws.cell_value(r,0)
    if not nm: continue
    fr = si(ws.cell_value(r,1)); to = si(ws.cell_value(r,2))
    length_ft = sf(ws.cell_value(r,3))
    config = si(ws.cell_value(r,9))
    length_km = length_ft / 5280.0 * 1.60934
    print(f"  {nm}: {fr}->{to}, {length_ft:.0f} ft = {length_km:.3f} km, config={config}")

print(f"\nUnit conversion: ohm/mile -> ohm/km = divide by 1.60934 (1 mile = 1.60934 km)")
print(f"Length conversion: ft -> km = ft/5280 * 1.60934")

# ============================================================
# 9. UNBALANCED LIMITATION
# ============================================================
print("\n" + "="*60)
print("9. UNBALANCED LIMITATION ASSESSMENT")
print("="*60)

print("""
The reference model (EPRI Windmil/OpenDSS) uses UNBALANCED 3-phase analysis:
  - Independent phase voltages (A, B, C)
  - Phase-specific loads (not all equal)
  - Phase-specific transformer connections (Y, D, open-D)
  - Phase-specific line impedances (asymmetric coupling)

Our model uses BALANCED positive-sequence analysis:
  - Single voltage per bus (assumes balanced 3-phase)
  - Total 3-phase power (sum of all phases)
  - Symmetrical component line impedances (Z1 only)
  - Cannot represent open-D regulators, single-phase loads, etc.

Impact on validation:
  - Per-phase voltages CANNOT be directly compared
  - The reference shows independent A/B/C voltages per bus
  - Our model shows a single pu voltage (average of 3 phases)
  - Voltage differences of 3-7% are EXPECTED for unbalanced feeders
  - The error is NOT entirely a modeling mistake

Key unbalanced elements that our model cannot represent:
  1. Single-phase loads on 3-phase feeders
  2. Open-delta regulator (Reg 5) - 2 of 3 phases
  3. Single-phase regulator (Reg 4) - only phase A
  4. Center-tapped transformers with unbalanced secondary loads
  5. Asymmetric line coupling (mutual impedance between phases)
""")

# ============================================================
# BUILD AND RUN MODEL
# ============================================================
print("\n" + "="*60)
print("BUILDING AND RUNNING MODEL")
print("="*60)

import build_feeder
# The build_feeder module already runs the power flow
# We'll load the saved network instead

net = pp.from_json(r'C:\Users\ASUS\Documents\suryaghar\feeder_network.json')
print(f"Loaded network: {len(net.bus)} buses, {len(net.line)} lines, {len(net.trafo)} trafos")

pp.runpp(net, algorithm='nr', calculate_voltage_angles=True,
         max_iteration=500, numba=False, tolerance_mva=1e-3,
         enforce_q_limits=False)
print("Power flow converged!")

# ============================================================
# 10. COMPREHENSIVE VALIDATION
# ============================================================
print("\n" + "="*60)
print("10. COMPREHENSIVE VALIDATION")
print("="*60)

# Read reference TXT
import re
ref_data = {}
with open(r'C:\Users\ASUS\Documents\suryaghar\IEEE_CompTestFeeder_Results_20140401.txt', 'r', encoding='latin-1') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('Windmil') or line.startswith('Bus Name') or '---' in line:
            continue
        parts = line.split()
        if len(parts) >= 10:
            bus_name = parts[0]
            # Extract base voltage from txt
            try:
                base_v = float(parts[4])
            except:
                continue
            # This is a data line
            if bus_name not in ref_data:
                ref_data[bus_name] = {}
            try:
                ref_data[bus_name]['base_v'] = float(parts[4])
                ref_data[bus_name]['base_120'] = float(parts[5])
                ref_data[bus_name]['element_drop'] = float(parts[6])
                ref_data[bus_name]['accum_drop'] = float(parts[7])
                ref_data[bus_name]['thru_amps'] = float(parts[8])
                ref_data[bus_name]['pct_cap'] = float(parts[9])
            except:
                pass

# Parse bus voltages from TXT
print("\nParsing reference TXT for bus voltages...")
ref_voltages = {}
with open(r'C:\Users\ASUS\Documents\suryaghar\IEEE_CompTestFeeder_Results_20140401.txt', 'r', encoding='latin-1') as f:
    in_bus_section = False
    for line in f:
        line = line.strip()
        if 'Bus Name' in line and 'Base kV' in line:
            in_bus_section = True
            continue
        if in_bus_section and ('---' in line or line == ''):
            in_bus_section = False
            continue
        if in_bus_section:
            parts = line.split()
            if len(parts) >= 3:
                bus_name = parts[0]
                try:
                    base_kv = float(parts[1])
                    base_120 = float(parts[2])
                    # Phase A voltage
                    va = float(parts[3])
                    ref_voltages[bus_name] = {'base_kv': base_kv, 'base_120': base_120, 'va_120': va}
                except:
                    pass

# Actually, let me parse the full TXT more carefully
print("Re-parsing reference TXT...")
ref_full = {}
with open(r'C:\Users\ASUS\Documents\suryaghar\IEEE_CompTestFeeder_Results_20140401.txt', 'r', encoding='latin-1') as f:
    lines = f.readlines()

# Find the bus voltage section
for i, line in enumerate(lines):
    if 'Bus Name' in line and 'Base kV' in line:
        # This is a header line, next lines are data
        for j in range(i+1, min(i+200, len(lines))):
            l = lines[j].strip()
            if not l or '---' in l:
                break
            parts = l.split()
            if len(parts) >= 5:
                bus = parts[0]
                try:
                    bkv = float(parts[1])
                    b120 = float(parts[2])
                    va = float(parts[3])
                    vb = float(parts[4])
                    vc = float(parts[5])
                    ref_full[bus] = {'bkv': bkv, 'b120': b120, 'va': va, 'vb': vb, 'vc': vc}
                except:
                    pass
        break

print(f"Found {len(ref_full)} bus entries in reference")

# Compare with model
print("\n--- Voltage Comparison (Phase A avg vs model) ---")
errors = []
for bus_name, ref_info in sorted(ref_full.items()):
    # Find matching bus in model
    pp_bus = None
    for idx in range(len(net.bus)):
        if net.bus.name.iloc[idx] == bus_name:
            pp_bus = idx
            break
    if pp_bus is None:
        continue
    vm_pu = net.res_bus.vm_pu.iloc[pp_bus]
    va_120 = ref_info['va']
    # Reference voltages are on 120V base
    ref_pu = va_120 / 120.0
    err_pct = (vm_pu - ref_pu) / ref_pu * 100
    errors.append((bus_name, vm_pu, ref_pu, err_pct))

if errors:
    errors.sort(key=lambda x: abs(x[3]), reverse=True)
    print(f"\n10 WORST VOLTAGE MISMATCHES:")
    for i, (bus, pp_v, ref_v, err) in enumerate(errors[:10]):
        print(f"  {i+1}. Bus {bus}: pp={pp_v:.4f} pu, ref={ref_v:.4f} pu, err={err:+.2f}%")

    mae = sum(abs(e[3]) for e in errors) / len(errors)
    rmse = math.sqrt(sum(e[3]**2 for e in errors) / len(errors))
    max_err = max(abs(e[3]) for e in errors)
    print(f"\n  MAE = {mae:.2f}%")
    print(f"  RMSE = {rmse:.2f}%")
    print(f"  Max error = {max_err:.2f}%")
    print(f"  Buses compared: {len(errors)}")

# Source comparison
print("\n--- Source Power ---")
ext_p = net.res_ext_grid.p_mw.iloc[0]
ext_q = net.res_ext_grid.q_mvar.iloc[0]
print(f"  Model: P={ext_p:.4f} MW, Q={ext_q:.4f} MVAR")
print(f"  Reference: P=4.139 MW, Q=1.316 MVAR")
print(f"  Error: P={(ext_p-4.139)/4.139*100:+.2f}%, Q={(ext_q-1.316)/1.316*100:+.2f}%")

# Transformer loading
print("\n--- Transformer Loading ---")
for idx in range(len(net.trafo)):
    name = net.trafo.name.iloc[idx]
    ld = net.res_trafo.loading_percent.iloc[idx]
    sn = net.trafo.sn_mva.iloc[idx]
    if not math.isnan(ld):
        flag = " *** OVERLOAD" if ld > 100 else ""
        print(f"  {name:>12s}: {ld:6.1f}% ({sn:.2f} MVA){flag}")

print("\n" + "="*60)
print("INVESTIGATION COMPLETE")
print("="*60)
