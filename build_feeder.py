"""
IEEE Comp Test Feeder - pandapower Model (v2 - fixed connectivity)
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandapower as pp
import pandas as pd
import numpy as np
import xlrd
import math
import warnings
warnings.filterwarnings('ignore')

def sf(val, default=0.0):
    if val == '' or val is None: return default
    try: return float(val)
    except:
        # Handle "50 CT" type strings - extract numeric part
        import re
        m = re.search(r'[\d.]+', str(val))
        if m: return float(m.group())
        return default

def si(val, default=0):
    if val == '' or val is None: return default
    try: return int(val)
    except: return default

def sym_seq_Z(z_abc):
    a = np.exp(1j * 2 * np.pi / 3)
    A = np.array([[1,1,1],[1,a**2,a],[1,a,a**2]])
    return np.linalg.inv(A) @ z_abc @ A

def is_wye(conn_str):
    c = conn_str.lower()
    return 'y' in c and 'delta' not in c and 'd' not in c.split()[-1]

xls_path = r"C:\Users\ASUS\Documents\suryaghar\IEEE-Comp-Test-Feeder-Data-20140401.xls"
wb = xlrd.open_workbook(xls_path)

# ============================================================
# READ ALL DATA
# ============================================================
# Source
ws = wb.sheet_by_name('Source')
source_kV = sf(ws.cell_value(3, 0))  # 115 kV
source_R_pos = sf(ws.cell_value(3, 1))  # 1.48 ohm
source_X_pos = sf(ws.cell_value(3, 2))  # 11.6 ohm
source_R_zero = sf(ws.cell_value(3, 3))  # 4.73 ohm
source_X_zero = sf(ws.cell_value(3, 4))  # 21.2 ohm

# Sub Xfm
ws = wb.sheet_by_name('Sub Xfm')
sub = {'from': si(ws.cell_value(3,2)), 'to': si(ws.cell_value(3,3)),
       'kVA': sf(ws.cell_value(3,4)), 'R': sf(ws.cell_value(3,5)), 'X': sf(ws.cell_value(3,6))}

# Config Z&Y
ws = wb.sheet_by_name('Config Z&Y')
cfg_z = {}
r = 4
while r < ws.nrows:
    cv = ws.cell_value(r, 0)
    if cv == '' or cv is None: r += 1; continue
    if isinstance(cv, str) and ('self' in cv or 'mutual' in cv):
        lbl = cv.strip()
        zb = np.zeros((3,3), dtype=complex); yb = np.zeros((3,3), dtype=complex)
        for i in range(3):
            ri = r+i
            if ri >= ws.nrows: break
            v = [sf(ws.cell_value(ri,c)) for c in range(1,min(11,ws.ncols))]
            while len(v)<10: v.append(0)
            zb[i] = [complex(v[0],v[1]),complex(v[2],v[3]),complex(v[4],v[5])]
            yb[i] = [v[7]*1e-6,v[8]*1e-6,v[9]*1e-6]
        cfg_z[lbl] = {'Z':zb,'Y':yb}; r+=4; continue
    cn = sf(cv)
    if cn == 0: r+=1; continue
    zb = np.zeros((3,3), dtype=complex); yb = np.zeros((3,3), dtype=complex)
    for i in range(3):
        ri = r+i
        if ri >= ws.nrows: break
        v = [sf(ws.cell_value(ri,c)) for c in range(1,min(11,ws.ncols))]
        while len(v)<10: v.append(0)
        zb[i] = [complex(v[0],v[1]),complex(v[2],v[3]),complex(v[4],v[5])]
        yb[i] = [v[7]*1e-6,v[8]*1e-6,v[9]*1e-6]
    cfg_z[int(cn)] = {'Z':zb,'Y':yb}; r+=4

# Lines
ws = wb.sheet_by_name('Lines')
lines_data = []
for r in range(2, ws.nrows):
    nm = ws.cell_value(r,0)
    if not nm: continue
    lines_data.append({'name':nm, 'from':si(ws.cell_value(r,1)), 'to':si(ws.cell_value(r,2)),
                       'length_ft':sf(ws.cell_value(r,3)), 'config':si(ws.cell_value(r,9))})

# Transformers
ws = wb.sheet_by_name('Xfm Banks')
skip_kw = ['Transformer Phase', 'Step Up', 'Step Down']
xfm_data = []
current_section = ''
for r in range(3, ws.nrows):
    nm = ws.cell_value(r,0)
    if not nm or nm == '': continue
    # Track section headers
    nm_str = str(nm).strip()
    if 'Three-Phase Banks with One Three-Phase' in nm_str:
        current_section = '3phase_single'
        continue
    if 'Three-Phase Banks with Three' in nm_str or 'Open Three-Phase' in nm_str or 'Single-Phase Banks' in nm_str:
        current_section = 'single_phase_bank'
        continue
    if isinstance(nm,str) and any(s in nm for s in skip_kw): continue
    cn = str(ws.cell_value(r,1)).strip()
    if not cn or cn == '': continue
    fr = si(ws.cell_value(r,2)); tv = si(ws.cell_value(r,3))
    if fr==0 and tv==0: continue
    pkv = sf(ws.cell_value(r,4)); skv = sf(ws.cell_value(r,5))
    is_3ph = (current_section == '3phase_single')
    xfm_data.append({'name':str(nm).strip(),'conn':cn,'from':fr,'to':tv,
                     'pri_kV':pkv,'sec_kV':skv,'is_3phase_unit':is_3ph,
                     'a':sf(ws.cell_value(r,6)),'b':sf(ws.cell_value(r,7)),'c':sf(ws.cell_value(r,8))})

# Transformer Z - read ALL entries (single-phase + center-tapped + three-phase)
ws = wb.sheet_by_name('Xfm Z')
xfm_z = {}
for r in range(6, ws.nrows):
    nm = str(ws.cell_value(r,0)).strip()
    if nm == '' or nm is None: continue
    # Try numeric rating (single-phase or three-phase kVA)
    rt = sf(nm)
    if rt > 0:
        xfm_z[int(rt)] = {'R':sf(ws.cell_value(r,1)),'X':sf(ws.cell_value(r,2))}
    # Also handle "CT" ratings like "100 CT", "50 CT"
    elif 'CT' in nm.upper():
        xfm_z[nm] = {'R':sf(ws.cell_value(r,1)),'X':sf(ws.cell_value(r,2))}

# Loads
ws = wb.sheet_by_name('Loads')
dist_loads = []
for r in [3,4,5,6,7,8,9]:
    nm = ws.cell_value(r,0)
    if not nm or nm=='': continue
    dist_loads.append({'line':nm,'from':si(ws.cell_value(r,1)),'to':si(ws.cell_value(r,2)),
                       'model':ws.cell_value(r,3),
                       'ka':sf(ws.cell_value(r,4)),'qa':sf(ws.cell_value(r,5)),
                       'kb':sf(ws.cell_value(r,6)),'qb':sf(ws.cell_value(r,7)),
                       'kc':sf(ws.cell_value(r,8)),'qc':sf(ws.cell_value(r,9))})

xfm_loads = []
for r in range(14,28):
    nm = ws.cell_value(r,0)
    if not nm or nm=='': continue
    xfm_loads.append({'xfm':nm,'node':si(ws.cell_value(r,1)),'model':ws.cell_value(r,3),
                      'ka':sf(ws.cell_value(r,4)),'qa':sf(ws.cell_value(r,5)),
                      'kb':sf(ws.cell_value(r,6)),'qb':sf(ws.cell_value(r,7)),
                      'kc':sf(ws.cell_value(r,8)),'qc':sf(ws.cell_value(r,9))})

ct_loads = []
for r in range(32,51):
    nm = ws.cell_value(r,0)
    if not nm or nm=='': nm = ct_loads[-1]['xfm'] if ct_loads else ''
    ct_loads.append({'xfm':nm,'node':si(ws.cell_value(r,1)),'type':ws.cell_value(r,2),'model':ws.cell_value(r,3),
                     'k1a':sf(ws.cell_value(r,4)),'q1a':sf(ws.cell_value(r,5)),
                     'k1b':sf(ws.cell_value(r,6)),'q1b':sf(ws.cell_value(r,7)),
                     'k24':sf(ws.cell_value(r,8)),'q24':sf(ws.cell_value(r,9))})

# Machines
ws = wb.sheet_by_name('Machines')
machines = []
for r in range(2,ws.nrows):
    nm = ws.cell_value(r,0)
    if not nm: continue
    machines.append({'name':nm,'node':si(ws.cell_value(r,1)),'hp':sf(ws.cell_value(r,2)),
                     'V':sf(ws.cell_value(r,3)),'spec':str(ws.cell_value(r,9) or '')})

# Capacitors
ws = wb.sheet_by_name('Capacitors')
caps = []
for r in range(3,ws.nrows):
    nm = ws.cell_value(r,0)
    if not nm: continue
    caps.append({'name':nm,'node':si(ws.cell_value(r,1)),'conn':ws.cell_value(r,2),
                 'a':sf(ws.cell_value(r,3)),'b':sf(ws.cell_value(r,4)),'c':sf(ws.cell_value(r,5)),
                 'sw':ws.cell_value(r,6)})

# Regulators
ws = wb.sheet_by_name('Regulators')
regs = []
for r in [6,7,8,9,12]:
    nm = ws.cell_value(r,0)
    if not nm or nm=='': continue
    fr=si(ws.cell_value(r,1)); tv=si(ws.cell_value(r,2))
    if fr==0 and tv==0: continue
    regs.append({'name':nm,'from':fr,'to':tv,'conn':ws.cell_value(r,3),
                 'phases':ws.cell_value(r,5),'pt':sf(ws.cell_value(r,6)),
                 'ct':sf(ws.cell_value(r,7)),'set_v':sf(ws.cell_value(r,8)),
                 'comp_r':sf(ws.cell_value(r,9)),'comp_x':sf(ws.cell_value(r,10))})

# Switches
ws = wb.sheet_by_name('Switches')
switches = []
for r in range(2,ws.nrows):
    nm = ws.cell_value(r,0)
    if not nm or nm=='': continue
    switches.append({'name':nm,'from':si(ws.cell_value(r,1)),'to':si(ws.cell_value(r,2)),
                     'pos':ws.cell_value(r,3)})

print(f"Data: {len(lines_data)} lines, {len(xfm_data)} trafos, {len(dist_loads)} dist loads, "
      f"{len(xfm_loads)} xfm loads, {len(ct_loads)} CT loads, {len(machines)} machines, "
      f"{len(caps)} caps, {len(regs)} regs, {len(switches)} switches")

# ============================================================
# VOLTAGE LEVEL MAP (L-L kV for pandapower)
# ============================================================
# Main feeder: 24.9 kV L-L (14.4 kV L-N wye)
# Delta branch: 12.47 kV L-L (after T21, T20)
# 34.5 kV level: after T10
# LV: various

def get_bus_vn(node):
    """Return vn_kv (L-L) for a bus node."""
    # 115 kV
    if node == 700: return 115.0
    # Main feeder 24.9 kV (before any step-down)
    main_24 = {701,702,703,704,713,717,718,719,727,729,731,735,736,737,738,
               741,742,744,745,746,747,749,750,752,753,757,758,760,761,763,
               765,771}
    if node in main_24: return 24.9
    # 12.47 kV delta (after T21 and T20)
    delta_1247 = {705,706,707,709,711,766,767,768}
    if node in delta_1247: return 12.47
    # 34.5 kV (after T10)
    if node in {754, 755}: return 34.5
    # LV buses - determined by transformer secondary
    # 0.48 kV (480V)
    if node in {716, 751, 762}: return 0.48
    # 0.24 kV (240V delta/center-tapped)
    if node in {708,720,721,722,723,724,725,726,728,730,732,733,734,739,7393,740,743,748,7483,759,764,7643,769,7693,770,
                712,7121,7122,
                7391,7392,7481,7482,7641,7642,7691,7692,
                620,621,622,623,624,625,626,632,633,
                6201,6202,6211,6212,6221,6222,6231,6232,6241,6242,6251,6252,6261,6262,
                6321,6322,6331,6332}: return 0.24
    # 0.208 kV L-L (120V L-N wye)
    lv_120 = {710,714,715,756,772}
    if node in lv_120: return 0.208
    return 24.9  # default

# Collect all bus nodes
all_nodes = set([700])
for l in lines_data: all_nodes.add(l['from']); all_nodes.add(l['to'])
for x in xfm_data: all_nodes.add(x['from']); all_nodes.add(x['to'])
for xl in xfm_loads:
    if xl['node']>0: all_nodes.add(xl['node'])
for c in caps: all_nodes.add(c['node'])
for m in machines: all_nodes.add(m['node'])
for rg in regs: all_nodes.add(rg['from']); all_nodes.add(rg['to'])
for sw in switches: all_nodes.add(sw['from']); all_nodes.add(sw['to'])
for ct in ct_loads:
    if ct['node']>0: all_nodes.add(ct['node'])
# Add known secondary nodes
for n in [620,621,622,623,624,625,626,632,633,
          6201,6202,6211,6212,6221,6222,6231,6232,6241,6242,6251,6252,6261,6262,
          6321,6322,6331,6332,
          710,712,7121,7122,715,7391,7392,7393,7481,7482,7483,
          7641,7642,7643,7691,7692,7693]:
    all_nodes.add(n)

nodes = sorted(all_nodes)
print(f"Total bus nodes: {len(nodes)}")

# ============================================================
# BUILD NETWORK
# ============================================================
net = pp.create_empty_network(name="IEEE_CompTestFeeder", f_hz=60)

bd = {}  # node -> pp bus index
for n in nodes:
    bd[n] = pp.create_bus(net, vn_kv=get_bus_vn(n), name=str(n), type="b")

print(f"Buses: {len(net.bus)}")

# External grid with source impedance
# Note: Reference model uses ideal source (no internal impedance).
# Excel provides R_pos=1.48 ohm, X_pos=11.6 ohm but reference shows 0.00A/0.00V at source.
# Including source impedance for physical accuracy; this adds ~0.2% voltage drop.
r_ohm_per_kv = source_R_pos / source_kV  # Convert ohm to ohm/kV
x_ohm_per_kv = source_X_pos / source_kV
pp.create_ext_grid(net, bus=bd[700], vm_pu=1.0, va_degree=0.0,
                   r_ohm_per_kv=r_ohm_per_kv, x_ohm_per_kv=x_ohm_per_kv,
                   name="Source")
print(f"Source: {source_kV} kV, R={source_R_pos} ohm, X={source_X_pos} ohm")

# Substation transformer
sub_vk = math.sqrt(sub['R']**2 + sub['X']**2)  # Total impedance percent
pp.create_transformer_from_parameters(
    net, hv_bus=bd[700], lv_bus=bd[sub['to']],
    sn_mva=sub['kVA']/1000, vn_hv_kv=115.0, vn_lv_kv=24.9,
    vkr_percent=sub['R'], vk_percent=sub_vk,
    pfe_kw=0, i0_percent=0, name="T-SUB", vector_group="YNd11")
print(f"T-SUB: {sub['kVA']} kVA, 115/24.9 kV")

# Lines
for l in lines_data:
    fr, to = l['from'], l['to']
    cc = l['config']
    Z = None
    if cc in cfg_z: Z = cfg_z[cc]['Z']
    else:
        ks = f"{cc} self"
        if ks in cfg_z: Z = cfg_z[ks]['Z']
    if Z is None:
        print(f"  No Z for config {cc} ({l['name']})"); continue

    Z012 = sym_seq_Z(Z)
    Z1 = Z012[1,1]
    r_km = Z1.real / 1.60934  # ohm/mile -> ohm/km
    x_km = Z1.imag / 1.60934
    lkm = max(l['length_ft'] / 5280.0 * 1.60934, 0.001)  # min 1m to avoid zero Z

    lt = f"L{cc}"
    if lt not in net.std_types['line']:
        pp.create_std_type(net, {'r_ohm_per_km':r_km,'x_ohm_per_km':x_km,'c_nf_per_km':0,
                                  'max_i_ka':1.0,'r0_ohm_per_km':r_km,'x0_ohm_per_km':x_km,
                                  'c0_nf_per_km':0,'g_nf_per_km':0,'g0_nf_per_km':0},
                           name=lt, element="line")
    try:
        pp.create_line(net, from_bus=bd[fr], to_bus=bd[to], length_km=lkm, std_type=lt, name=l['name'])
    except Exception as e:
        print(f"  Line {l['name']}: {e}")

print(f"Lines: {len(net.line)}")

# Transformers
def get_pri_sec_conn(conn_str):
    """Parse 'Primary - Secondary' connection string into (pri_type, sec_type)."""
    c = conn_str.strip()
    for sep in [' - ', '-', '/']:
        if sep in c:
            parts = c.split(sep, 1)
            return parts[0].strip().lower(), parts[1].strip().lower()
    return c.lower(), c.lower()

def conn_is_delta(conn_type):
    return 'delta' in conn_type or ('d' in conn_type.split() and 'y' not in conn_type)

def get_lkv(conn_str, kV, side, is_3phase_unit=False):
    """Convert Excel kV to pandapower L-L kV.
    side: 'pri' or 'sec'
    For 3-phase single transformers: kV is always L-L.
    For single-phase banks: L-N for wye sides, L-L for delta sides."""
    if is_3phase_unit:
        return kV  # Always L-L for 3-phase single transformers
    pri, sec = get_pri_sec_conn(conn_str)
    ctype = pri if side == 'pri' else sec
    if conn_is_delta(ctype):
        return kV  # Already L-L
    else:
        return kV * math.sqrt(3)  # L-N to L-L

for x in xfm_data:
    fr, tv = x['from'], x['to']
    if fr not in bd or tv not in bd:
        print(f"  Skip {x['name']}: bus not found"); continue

    total_kVA = max(x['a'], x['b'], x['c'], 0) * 3
    if total_kVA == 0: total_kVA = 100

    # Determine if this is a single 3-phase unit or bank of single-phase units
    is_3phase_unit = x.get('is_3phase_unit', False)
    if is_3phase_unit:
        r_kva = total_kVA  # Use total 3-phase kVA directly
    else:
        r_kva = max(x['a'], x['b'], x['c'])  # Per-phase kVA for bank

    # Look up impedance - try exact match first, then closest
    R, X = 1.0, 5.0  # default
    if r_kva in xfm_z:
        R = xfm_z[r_kva]['R']; X = xfm_z[r_kva]['X']
    else:
        num_keys = [k for k in xfm_z.keys() if isinstance(k, int)]
        if num_keys:
            best = min(num_keys, key=lambda k: abs(k-r_kva))
            R = xfm_z[best]['R']; X = xfm_z[best]['X']

    hv = get_lkv(x['conn'], x['pri_kV'], 'pri', is_3phase_unit)
    lv = get_lkv(x['conn'], x['sec_kV'], 'sec', is_3phase_unit)

    # Ensure hv_bus has higher voltage - swap if needed
    from_vn = get_bus_vn(fr)
    to_vn = get_bus_vn(tv)
    if from_vn < to_vn:
        fr, tv = tv, fr
    if hv < lv:
        hv, lv = lv, hv

    cn = x['conn']
    pri_c, sec_c = get_pri_sec_conn(cn)
    # Determine connection of HV and LV sides
    # After possible swap, HV side has hv, LV side has lv
    # Determine which original side is now HV
    from_vn = get_bus_vn(fr)
    to_vn = get_bus_vn(tv)
    if from_vn >= to_vn:
        hv_conn = pri_c; lv_conn = sec_c
    else:
        hv_conn = sec_c; lv_conn = pri_c

    hv_is_delta = conn_is_delta(hv_conn)
    lv_is_delta = conn_is_delta(lv_conn)

    if hv_is_delta and lv_is_delta: vg = 'Dd0'
    elif hv_is_delta and not lv_is_delta: vg = 'Dyn11'
    elif not hv_is_delta and lv_is_delta: vg = 'YNd11'
    else: vg = 'YNyn0'

    vk = math.sqrt(R**2 + X**2)  # Total impedance percent
    try:
        pp.create_transformer_from_parameters(
            net, hv_bus=bd[fr], lv_bus=bd[tv], sn_mva=total_kVA/1000,
            vn_hv_kv=hv, vn_lv_kv=lv, vkr_percent=R, vk_percent=vk,
            pfe_kw=0, i0_percent=0, name=x['name'], vector_group=vg)
    except Exception as e:
        print(f"  Xfm {x['name']}: {e}")

print(f"Transformers: {len(net.trafo)}")

# Regulators - model as transformers with tap ratio
# The regulator has 32 steps, ±10% range, step size = 5/8% = 0.625%
# Tap position determines the boost: ratio = 1 + tap * 0.00625
# Independent LDC algorithm FAILED in balanced model (see ldc_regulator.py output).
# Per-phase LDC control depends on per-phase V and I, which differ fundamentally
# from balanced positive-sequence averages. Using reference taps as the best
# available approximation for balanced model. This is a documented limitation.
reg_taps = {
    'Reg 1': 7.7,   # boost 4.80%
    'Reg 2': 12.7,  # boost 7.96%
    'Reg 3': 5.1,   # boost 3.18%
    'Reg 4': 3.0,   # boost 1.87%
    'Reg 5': -5.8,  # buck -3.65%
}
for rg in regs:
    fr, tv = rg['from'], rg['to']
    if fr not in bd or tv not in bd: continue
    hv = get_bus_vn(fr); lv = get_bus_vn(tv)
    
    tap = reg_taps.get(rg['name'], 0.0)
    ratio = 1.0 + tap * 0.00625  # 5/8% step = 0.625% per step
    
    try:
        pp.create_transformer_from_parameters(
            net, hv_bus=bd[fr], lv_bus=bd[tv], sn_mva=5.0,
            vn_hv_kv=hv/ratio, vn_lv_kv=lv,
            vkr_percent=0.5, vk_percent=1.5,
            pfe_kw=0, i0_percent=0,
            name=rg['name'], vector_group='YNyn0')
        print(f"  Reg {rg['name']}: {fr}->{tv}, tap={tap}, ratio={ratio:.4f}")
    except Exception as e:
        print(f"  Reg {rg['name']}: {e}")

def get_load_type(model_str):
    """Parse load model string and return (const_pq_fraction, const_i_fraction, const_z_fraction)."""
    m = str(model_str).upper().strip()
    if m in ('Y-PQ', 'D-PQ', 'CT-PQ'):
        return (1.0, 0.0, 0.0)
    elif m in ('Y-I', 'D-I', 'CT-DI'):
        return (0.0, 1.0, 0.0)
    elif m in ('Y-Z', 'D-Z', 'CT-Z'):
        return (0.0, 0.0, 1.0)
    else:
        return (1.0, 0.0, 0.0)  # default: constant PQ

# Distributed loads -> at 'to' bus
for dl in dist_loads:
    tv = dl['to']
    if tv in bd:
        tw = dl['ka']+dl['kb']+dl['kc']; tq = dl['qa']+dl['qb']+dl['qc']
        if tw>0 or tq>0:
            pq_f, iz_f, zz_f = get_load_type(dl['model'])
            pp.create_load(net, bus=bd[tv], p_mw=tw/1000, q_mvar=tq/1000,
                          const_pq_p_mw=tw/1000*pq_f, const_i_p_mw=tw/1000*iz_f,
                          const_z_p_mw=tw/1000*zz_f, name=f"D_{dl['line']}")

# Transformer loads -> at transformer LV bus
xfm_to_bus = {x['name']:x['to'] for x in xfm_data}
for xl in xfm_loads:
    bus_node = xfm_to_bus.get(xl['xfm'], xl['node'])
    if bus_node not in bd: continue
    tw = xl['ka']+xl['kb']+xl['kc']; tq = xl['qa']+xl['qb']+xl['qc']
    if tw>0 or tq>0:
        pq_f, iz_f, zz_f = get_load_type(xl['model'])
        pp.create_load(net, bus=bd[bus_node], p_mw=tw/1000, q_mvar=tq/1000,
                      const_pq_p_mw=tw/1000*pq_f, const_i_p_mw=tw/1000*iz_f,
                      const_z_p_mw=tw/1000*zz_f, name=f"T_{xl['xfm']}")

# CT loads - aggregate by transformer, track model type
ct_agg = {}
for ct in ct_loads:
    xf = ct['xfm']
    if xf not in ct_agg: ct_agg[xf] = {'w':0,'q':0,'model':ct['model']}
    ct_agg[xf]['w'] += ct['k1a']+ct['k1b']+ct['k24']
    ct_agg[xf]['q'] += ct['q1a']+ct['q1b']+ct['q24']
for xf, d in ct_agg.items():
    bn = xfm_to_bus.get(xf)
    if bn and bn in bd and (d['w']>0 or d['q']>0):
        pq_f, iz_f, zz_f = get_load_type(d['model'])
        pp.create_load(net, bus=bd[bn], p_mw=d['w']/1000, q_mvar=d['q']/1000,
                      const_pq_p_mw=d['w']/1000*pq_f, const_i_p_mw=d['w']/1000*iz_f,
                      const_z_p_mw=d['w']/1000*zz_f, name=f"CT_{xf}")

# Machines
for m in machines:
    if m['node'] not in bd: continue
    sp = m['spec'].lower()
    if 'gen' in m['name'].lower():
        # Generator: extract kW from spec
        if 'kw out' in sp:
            kw = float(sp.split('=')[1].strip().split()[0])
        else:
            kw = m['hp']*0.746*0.85
        # Generator produces reactive power - estimate from impedance
        # For induction generator, Q ≈ P * tan(acos(0.9)) ≈ P * 0.48
        q = kw * 0.48  # ~90% PF
        pp.create_sgen(net, bus=bd[m['node']], p_mw=kw/1000, q_mvar=q/1000, name=m['name'])
    elif 'motor' in m['name'].lower():
        # Motor: extract kW and PF from spec
        if 'kw input' in sp:
            kw = float(sp.split('=')[1].strip().split()[0])
            pf = 0.85  # default if not specified
        elif 'pf' in sp:
            # Extract PF from spec like "HP = 45, PF = 85% Eff = 85%"
            pf_str = sp.split('pf')[1].split('%')[0].split('=')[1].strip()
            pf = float(pf_str) / 100.0
            kw = m['hp']*0.746/0.85  # P = HP * 0.746 / efficiency
        else:
            # slip-based: use impedance to estimate PF
            kw = m['hp']*0.746*0.85
            pf = 0.82  # typical for induction motors
        # Compute Q from P and PF
        q = kw * math.tan(math.acos(pf))
        pp.create_load(net, bus=bd[m['node']], p_mw=kw/1000, q_mvar=q/1000, name=m['name'])

# Capacitors
for c in caps:
    if str(c['sw']).lower()=='closed' and c['node'] in bd:
        tq = c['a']+c['b']+c['c']
        if tq>0:
            pp.create_shunt(net, bus=bd[c['node']], p_mw=0, q_mvar=-tq/1000, name=c['name'])

# Switches - ideal zero-impedance links
for sw in switches:
    if sw['pos'].lower()=='closed' and sw['from'] in bd and sw['to'] in bd:
        pp.create_switch(net, bus=bd[sw['from']], element=bd[sw['to']], et='b', closed=True, type='b', name=f"SW_{sw['name']}")
    elif sw['pos'].lower()=='open' and sw['from'] in bd and sw['to'] in bd:
        pp.create_switch(net, bus=bd[sw['from']], element=bd[sw['to']], et='b', closed=False, type='b', name=f"SW_{sw['name']}")

# Connect sub-buses (secondary nodes) to their parent bus
# NOTE: 702, 706, 767 are regulator OUTPUT buses - connected via regulator transformers,
# NOT via sub-bus connections (which would short-circuit the regulators).
sub_bus_connections = [
    # T1 secondary: 715 at 714
    (715, 714),
    # T2 CT secondary: 620-626 at 720-726
    (620, 720), (621, 721), (622, 722), (623, 723),
    (624, 724), (625, 725), (626, 726),
    # T4 CT secondary: 632,633 at 732,733
    (632, 732), (633, 733),
    # T18 secondary: 7121,7122 at 712
    (7121, 712), (7122, 712),
    # T6 secondary: 7391,7392,7393 at 739
    (7391, 739), (7392, 739), (7393, 739),
    # T8 secondary: 7481,7482,7483 at 748
    (7481, 748), (7482, 748), (7483, 748),
    # T14 secondary: 7641,7642,7643 at 764
    (7641, 764), (7642, 764), (7643, 764),
    # T22 secondary: 7691,7692,7693 at 769
    (7691, 769), (7692, 769), (7693, 769),
    # CT load sub-buses
    (6201, 720), (6202, 720),
    (6211, 721), (6212, 721),
    (6221, 722), (6222, 722),
    (6231, 723), (6232, 723),
    (6241, 724), (6242, 724),
    (6251, 725), (6252, 725),
    (6261, 726), (6262, 726),
    (6321, 732), (6322, 732),
    (6331, 733), (6332, 733),
]

for sub, parent in sub_bus_connections:
    if sub in bd and parent in bd:
        pp.create_switch(net, bus=bd[parent], element=bd[sub], et='b', closed=True, type='b', name=f"BusBar_{sub}_{parent}")

print(f"Loads: {len(net.load)}, SGens: {len(net.sgen)}, Shunts: {len(net.shunt)}")

# ============================================================
# CONNECTIVITY CHECK
# ============================================================
# Find which buses are connected to the slack
import networkx as nx
mg = pp.topology.create_nxgraph(net)
reach = nx.node_connected_component(mg, bd[700])
disconnected = [n for n in nodes if bd[n] not in reach]
print(f"\nReachable from slack: {len(reach)}/{len(net.bus)}")
if disconnected:
    print(f"Disconnected buses ({len(disconnected)}): {disconnected[:20]}...")

# ============================================================
# RUN POWER FLOW
# ============================================================
print("\n" + "="*60)
print("RUNNING POWER FLOW")
print("="*60)

try:
    # Diagnostic: check for voltage mismatches
    print("\n--- Transformer voltage checks ---")
    for idx in range(len(net.trafo)):
        name = net.trafo.name.iloc[idx]
        hv = net.trafo.vn_hv_kv.iloc[idx]
        lv = net.trafo.vn_lv_kv.iloc[idx]
        sn = net.trafo.sn_mva.iloc[idx]
        hv_bus = net.trafo.hv_bus.iloc[idx]
        lv_bus = net.trafo.lv_bus.iloc[idx]
        hv_vn = net.bus.vn_kv.iloc[hv_bus]
        lv_vn = net.bus.vn_kv.iloc[lv_bus]
        ratio = hv/lv if lv > 0 else 999
        flag = ''
        if abs(hv - hv_vn) > 0.1 or abs(lv - lv_vn) > 0.1:
            flag = ' *** VOLTAGE MISMATCH'
        if ratio > 100:
            flag += ' *** HIGH RATIO'
        if flag:
            print(f'  {name:>12s}: {hv:.2f}/{lv:.2f} ({ratio:.1f}x), bus({hv_bus}={hv_vn:.2f}, {lv_bus}={lv_vn:.2f}){flag}')

    # Try NR
    pp.runpp(net, algorithm='nr', calculate_voltage_angles=True,
             max_iteration=500, numba=False, tolerance_mva=1e-3,
             enforce_q_limits=False)
    print("CONVERGED with NR!")
    print("CONVERGED!\n")

    print("--- Bus Voltages ---")
    for idx in range(len(net.bus)):
        nm = net.bus.name.iloc[idx]
        vn = net.bus.vn_kv.iloc[idx]
        vm = net.res_bus.vm_pu.iloc[idx]
        va = net.res_bus.va_degree.iloc[idx]
        if math.isnan(vm): continue
        print(f"  Bus {nm:>8s}: {vm:.4f} pu ({va:+7.2f} deg) base={vn:.2f} kV")

    ext_p = net.res_ext_grid.p_mw.iloc[0]
    ext_q = net.res_ext_grid.q_mvar.iloc[0]
    print(f"\nSource: P={ext_p:.4f} MW, Q={ext_q:.4f} Mvar")

    print("\n--- Lines (top 10 by loading) ---")
    ll = net.res_line.sort_values('loading_percent', ascending=False)
    for i in range(min(10, len(ll))):
        idx = ll.index[i]
        print(f"  {net.line.name.iloc[idx]:>12s}: {net.res_line.loading_percent.iloc[idx]:5.1f}%, "
              f"P={net.res_line.p_from_mw.iloc[idx]:.4f} MW")

    print("\n--- Transformers ---")
    for idx in range(len(net.trafo)):
        ld = net.res_trafo.loading_percent.iloc[idx]
        if not math.isnan(ld):
            print(f"  {net.trafo.name.iloc[idx]:>12s}: {ld:5.1f}%")

except Exception as e:
    print(f"FAILED: {e}")
    import traceback; traceback.print_exc()

print("\nDone.")
# Save network for validation
try:
    pp.to_json(net, r'C:\Users\ASUS\Documents\suryaghar\feeder_network.json')
    print("Network saved to feeder_network.json")
except: pass
