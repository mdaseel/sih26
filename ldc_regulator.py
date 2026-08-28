"""
IEEE Comprehensive Test Feeder - Independent LDC Regulator Algorithm
Replaces hard-coded TXT taps with iterative Line Drop Compensation.
Uses ONLY Excel data for tap computation.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandapower as pp
import numpy as np
import xlrd
import math
import copy
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONSTANTS
# ============================================================
TAP_STEP = 0.00625      # 5/8% = 0.625% per step
TAP_MAX = 32            # ±32 steps
BANDWIDTH_V = 2.0       # 2V deadband
MAX_ITER = 50           # maximum LDC iterations
CT_SECONDARY_A = 5.0    # standard CT secondary current

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def sf(val, default=0.0):
    if val == '' or val is None: return default
    try: return float(val)
    except:
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

def conn_is_delta(conn_type):
    return 'delta' in conn_type or ('d' in conn_type and 'y' not in conn_type)

# ============================================================
# READ EXCEL DATA
# ============================================================
xls_path = r"C:\Users\ASUS\Documents\suryaghar\IEEE-Comp-Test-Feeder-Data-20140401.xls"
wb = xlrd.open_workbook(xls_path)

# Source
ws = wb.sheet_by_name('Source')
source_kV = sf(ws.cell_value(3, 0))
source_R_pos = sf(ws.cell_value(3, 1))
source_X_pos = sf(ws.cell_value(3, 2))

# Sub Xfm
ws = wb.sheet_by_name('Sub Xfm')
substation = {'from': si(ws.cell_value(3,2)), 'to': si(ws.cell_value(3,3)),
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
    nm_str = str(nm).strip()
    if 'Three-Phase Banks with One Three-Phase' in nm_str:
        current_section = '3phase_single'; continue
    if 'Three-Phase Banks with Three' in nm_str or 'Open Three-Phase' in nm_str or 'Single-Phase Banks' in nm_str:
        current_section = 'single_phase_bank'; continue
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

# Transformer Z
ws = wb.sheet_by_name('Xfm Z')
xfm_z = {}
for r in range(6, ws.nrows):
    nm = str(ws.cell_value(r,0)).strip()
    if nm == '' or nm is None: continue
    rt = sf(nm)
    if rt > 0:
        xfm_z[int(rt)] = {'R':sf(ws.cell_value(r,1)),'X':sf(ws.cell_value(r,2))}
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

# Also read Reg 5 bc phase data from row 13
reg5_bc = {'pt':sf(ws.cell_value(13,6)), 'ct':sf(ws.cell_value(13,7)),
           'set_v':sf(ws.cell_value(13,8)), 'comp_r':sf(ws.cell_value(13,9)),
           'comp_x':sf(ws.cell_value(13,10))}

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
# VOLTAGE LEVEL MAP
# ============================================================
def get_bus_vn(node):
    if node == 700: return 115.0
    main_24 = {701,702,703,704,713,717,718,719,727,729,731,735,736,737,738,
               741,742,744,745,746,747,749,750,752,753,757,758,760,761,763,
               765,771}
    if node in main_24: return 24.9
    delta_1247 = {705,706,707,709,711,766,767,768}
    if node in delta_1247: return 12.47
    if node in {754, 755}: return 34.5
    if node in {716, 751, 762}: return 0.48
    lv_024 = {708,720,721,722,723,724,725,726,728,730,732,733,734,739,7393,740,743,748,7483,759,764,7643,769,7693,770,
              712,7121,7122,
              7391,7392,7481,7482,7641,7642,7691,7692,
              620,621,622,623,624,625,626,632,633,
              6201,6202,6211,6212,6221,6222,6231,6232,6241,6242,6251,6252,6261,6262,
              6321,6322,6331,6332}
    if node in lv_024: return 0.24
    lv_120 = {710,714,715,756,772}
    if node in lv_120: return 0.208
    return 24.9

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
for n in [620,621,622,623,624,625,626,632,633,
          6201,6202,6211,6212,6221,6222,6231,6232,6241,6242,6251,6252,6261,6262,
          6321,6322,6331,6332,
          710,712,7121,7122,715,7391,7392,7393,7481,7482,7483,
          7641,7642,7643,7691,7692,7693]:
    all_nodes.add(n)

nodes = sorted(all_nodes)
print(f"Total bus nodes: {len(nodes)}")

# ============================================================
# BUILD NETWORK (base network without regulators)
# ============================================================
def build_network(reg_taps):
    """Build the full network with specified regulator taps.
    Returns (net, bus_dict, reg_info_list)"""
    net = pp.create_empty_network(name="IEEE_CompTestFeeder", f_hz=60)
    
    bd = {}
    for n in nodes:
        bd[n] = pp.create_bus(net, vn_kv=get_bus_vn(n), name=str(n), type="b")
    
    # External grid with source impedance
    r_ohm_per_kv = source_R_pos / source_kV
    x_ohm_per_kv = source_X_pos / source_kV
    pp.create_ext_grid(net, bus=bd[700], vm_pu=1.0, va_degree=0.0,
                       r_ohm_per_kv=r_ohm_per_kv, x_ohm_per_kv=x_ohm_per_kv,
                       name="Source")
    
    # Substation transformer
    sub_vk = math.sqrt(substation['R']**2 + substation['X']**2)
    pp.create_transformer_from_parameters(
        net, hv_bus=bd[700], lv_bus=bd[substation['to']],
        sn_mva=substation['kVA']/1000, vn_hv_kv=115.0, vn_lv_kv=24.9,
        vkr_percent=substation['R'], vk_percent=sub_vk,
        pfe_kw=0, i0_percent=0, name="T-SUB", vector_group="YNd11")
    
    # Lines
    for l in lines_data:
        fr, to = l['from'], l['to']
        cc = l['config']
        Z = None
        if cc in cfg_z: Z = cfg_z[cc]['Z']
        else:
            ks = f"{cc} self"
            if ks in cfg_z: Z = cfg_z[ks]['Z']
        if Z is None: continue
        Z012 = sym_seq_Z(Z)
        Z1 = Z012[1,1]
        r_km = Z1.real / 1.60934
        x_km = Z1.imag / 1.60934
        lkm = max(l['length_ft'] / 5280.0 * 1.60934, 0.001)
        lt = f"L{cc}"
        if lt not in net.std_types['line']:
            pp.create_std_type(net, {'r_ohm_per_km':r_km,'x_ohm_per_km':x_km,'c_nf_per_km':0,
                                      'max_i_ka':1.0,'r0_ohm_per_km':r_km,'x0_ohm_per_km':x_km,
                                      'c0_nf_per_km':0,'g_nf_per_km':0,'g0_nf_per_km':0},
                               name=lt, element="line")
        try:
            pp.create_line(net, from_bus=bd[fr], to_bus=bd[to], length_km=lkm, std_type=lt, name=l['name'])
        except: pass
    
    # Regular transformers
    def get_pri_sec_conn(conn_str):
        c = conn_str.strip()
        for sep in [' - ', '-', '/']:
            if sep in c:
                parts = c.split(sep, 1)
                return parts[0].strip().lower(), parts[1].strip().lower()
        return c.lower(), c.lower()
    
    def get_lkv(conn_str, kV, side, is_3phase_unit=False):
        if is_3phase_unit: return kV
        pri, sec = get_pri_sec_conn(conn_str)
        ctype = pri if side == 'pri' else sec
        if conn_is_delta(ctype): return kV
        else: return kV * math.sqrt(3)
    
    for x in xfm_data:
        fr, tv = x['from'], x['to']
        if fr not in bd or tv not in bd: continue
        total_kVA = max(x['a'], x['b'], x['c'], 0) * 3
        if total_kVA == 0: total_kVA = 100
        is_3phase_unit = x.get('is_3phase_unit', False)
        if is_3phase_unit: r_kva = total_kVA
        else: r_kva = max(x['a'], x['b'], x['c'])
        R, X = 1.0, 5.0
        if r_kva in xfm_z:
            R = xfm_z[r_kva]['R']; X = xfm_z[r_kva]['X']
        else:
            num_keys = [k for k in xfm_z.keys() if isinstance(k, int)]
            if num_keys:
                best = min(num_keys, key=lambda k: abs(k-r_kva))
                R = xfm_z[best]['R']; X = xfm_z[best]['X']
        hv = get_lkv(x['conn'], x['pri_kV'], 'pri', is_3phase_unit)
        lv = get_lkv(x['conn'], x['sec_kV'], 'sec', is_3phase_unit)
        from_vn = get_bus_vn(fr)
        to_vn = get_bus_vn(tv)
        if from_vn < to_vn: fr, tv = tv, fr
        if hv < lv: hv, lv = lv, hv
        cn = x['conn']
        pri_c, sec_c = get_pri_sec_conn(cn)
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
        vk = math.sqrt(R**2 + X**2)
        try:
            pp.create_transformer_from_parameters(
                net, hv_bus=bd[fr], lv_bus=bd[tv], sn_mva=total_kVA/1000,
                vn_hv_kv=hv, vn_lv_kv=lv, vkr_percent=R, vk_percent=vk,
                pfe_kw=0, i0_percent=0, name=x['name'], vector_group=vg)
        except: pass
    
    # Regulators - model as transformers with tap ratio
    reg_info = []
    for rg in regs:
        fr, tv = rg['from'], rg['to']
        if fr not in bd or tv not in bd: continue
        hv = get_bus_vn(fr); lv = get_bus_vn(tv)
        tap = reg_taps.get(rg['name'], 0.0)
        ratio = 1.0 + tap * TAP_STEP
        try:
            pp.create_transformer_from_parameters(
                net, hv_bus=bd[fr], lv_bus=bd[tv], sn_mva=5.0,
                vn_hv_kv=hv/ratio, vn_lv_kv=lv,
                vkr_percent=0.5, vk_percent=1.5,
                pfe_kw=0, i0_percent=0,
                name=rg['name'], vector_group='YNyn0')
            reg_info.append({'name': rg['name'], 'from': fr, 'to': tv,
                             'hv_kv': hv, 'lv_kv': lv, 'tap': tap, 'ratio': ratio,
                             'pt': rg['pt'], 'ct': rg['ct'], 'set_v': rg['set_v'],
                             'comp_r': rg['comp_r'], 'comp_x': rg['comp_x'],
                             'conn': rg['conn'], 'phases': rg['phases'],
                             'trafo_idx': len(net.trafo) - 1})
        except: pass
    
    # Load types
    def get_load_type(model_str):
        m = str(model_str).upper().strip()
        if m in ('Y-PQ', 'D-PQ', 'CT-PQ'): return (1.0, 0.0, 0.0)
        elif m in ('Y-I', 'D-I', 'CT-DI'): return (0.0, 1.0, 0.0)
        elif m in ('Y-Z', 'D-Z', 'CT-Z'): return (0.0, 0.0, 1.0)
        else: return (1.0, 0.0, 0.0)
    
    # Distributed loads
    for dl in dist_loads:
        tv = dl['to']
        if tv in bd:
            tw = dl['ka']+dl['kb']+dl['kc']; tq = dl['qa']+dl['qb']+dl['qc']
            if tw>0 or tq>0:
                pq_f, iz_f, zz_f = get_load_type(dl['model'])
                pp.create_load(net, bus=bd[tv], p_mw=tw/1000, q_mvar=tq/1000,
                               const_pq_p_mw=tw/1000*pq_f, const_i_p_mw=tw/1000*iz_f,
                               const_z_p_mw=tw/1000*zz_f, name=f"D_{dl['line']}")
    
    # Transformer loads
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
    
    # CT loads
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
            if 'kw out' in sp:
                kw = float(sp.split('=')[1].strip().split()[0])
            else:
                kw = m['hp']*0.746*0.85
            q = kw * 0.48
            pp.create_sgen(net, bus=bd[m['node']], p_mw=kw/1000, q_mvar=q/1000, name=m['name'])
        elif 'motor' in m['name'].lower():
            if 'kw input' in sp:
                kw = float(sp.split('=')[1].strip().split()[0])
                pf = 0.85
            elif 'pf' in sp:
                pf_str = sp.split('pf')[1].split('%')[0].split('=')[1].strip()
                pf = float(pf_str) / 100.0
                kw = m['hp']*0.746/0.85
            else:
                kw = m['hp']*0.746*0.85
                pf = 0.82
            q = kw * math.tan(math.acos(pf))
            pp.create_load(net, bus=bd[m['node']], p_mw=kw/1000, q_mvar=q/1000, name=m['name'])
    
    # Capacitors
    for c in caps:
        if str(c['sw']).lower()=='closed' and c['node'] in bd:
            tq = c['a']+c['b']+c['c']
            if tq>0:
                pp.create_shunt(net, bus=bd[c['node']], p_mw=0, q_mvar=-tq/1000, name=c['name'])
    
    # Switches
    for sw in switches:
        if sw['pos'].lower()=='closed' and sw['from'] in bd and sw['to'] in bd:
            pp.create_switch(net, bus=bd[sw['from']], element=bd[sw['to']], et='b', closed=True, type='b', name=f"SW_{sw['name']}")
        elif sw['pos'].lower()=='open' and sw['from'] in bd and sw['to'] in bd:
            pp.create_switch(net, bus=bd[sw['from']], element=bd[sw['to']], et='b', closed=False, type='b', name=f"SW_{sw['name']}")
    
    # Sub-bus connections
    sub_bus_connections = [
        (715, 714),
        (620, 720), (621, 721), (622, 722), (623, 723),
        (624, 724), (625, 725), (626, 726),
        (632, 732), (633, 733),
        (7121, 712), (7122, 712),
        (7391, 739), (7392, 739), (7393, 739),
        (7481, 748), (7482, 748), (7483, 748),
        (7641, 764), (7642, 764), (7643, 764),
        (7691, 769), (7692, 769), (7693, 769),
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
    for sb, parent in sub_bus_connections:
        if sb in bd and parent in bd:
            pp.create_switch(net, bus=bd[parent], element=bd[sb], et='b', closed=True, type='b', name=f"BusBar_{sb}_{parent}")
    
    return net, bd, reg_info

def run_pf(net):
    """Run power flow, return True if converged."""
    try:
        pp.runpp(net, algorithm='nr', calculate_voltage_angles=True,
                 max_iteration=500, numba=False, tolerance_mva=1e-3,
                 enforce_q_limits=False)
        return True
    except:
        return False

def compute_ldc_voltage(net, reg_info, bd):
    """Compute the LDC compensated voltage for a regulator.
    
    Uses the standard LDC formula:
        V_comp = V_pt + I_ct * (CompR + j*CompX)
    
    Where:
        V_pt = V_out_pu * PT  (volts, on PT secondary)
        I_ct = I_actual * (CT_SECONDARY_A / CT_rating)  (amps, on CT secondary)
        CompR, CompX = ohms on PT/CT secondary base
    
    Returns (V_comp_magnitude_volts, V_pt_volts, I_ct_amps, V_comp_complex)
    """
    trafo_idx = reg_info['trafo_idx']
    pp_lv_bus = bd[reg_info['to']]
    pt = reg_info['pt']
    ct = reg_info['ct']
    comp_r = reg_info['comp_r']
    comp_x = reg_info['comp_x']
    v_base_kv = reg_info['lv_kv']  # L-L kV
    
    # Regulator output bus voltage
    v_out_pu = net.res_bus.vm_pu.iloc[pp_lv_bus]
    v_out_angle_deg = net.res_bus.va_degree.iloc[pp_lv_bus]
    v_out_angle_rad = math.radians(v_out_angle_deg)
    
    # Complex voltage at output bus (kV, L-L)
    v_out_complex_kv = v_out_pu * v_base_kv * np.exp(1j * v_out_angle_rad)
    
    # Power flowing from regulator to load (MVA)
    p_out_mw = -net.res_trafo.p_lv_mw.iloc[trafo_idx]
    q_out_mvar = -net.res_trafo.q_lv_mvar.iloc[trafo_idx]
    s_out_mva = complex(p_out_mw, q_out_mvar)
    
    # Current in per-unit
    v_out_pu_complex = v_out_pu * np.exp(1j * v_out_angle_rad)
    s_out_pu = s_out_mva / 5.0  # 5 MVA base for regulator
    i_out_pu = np.conj(s_out_pu / v_out_pu_complex)
    
    # Actual current in kA
    i_base_ka = 5.0 / (v_base_kv * math.sqrt(3))
    i_out_ka = i_out_pu * i_base_ka
    i_out_a = i_out_ka * 1000
    
    # Current on CT secondary
    i_ct_a = i_out_a * (CT_SECONDARY_A / ct)
    
    # PT secondary voltage
    v_pt_v = v_out_pu * pt
    
    # Compensated voltage (complex)
    z_comp = complex(comp_r, comp_x)
    v_comp_complex = v_pt_v + i_ct_a * z_comp
    
    # CRITICAL: SetV is ALWAYS on 120V base (distribution convention).
    # For PT!=120, normalize V_comp to 120V base before comparing with SetV.
    v_comp_normalized = v_comp_complex * (120.0 / pt)
    v_comp_mag = abs(v_comp_normalized)
    
    return v_comp_mag, v_pt_v, i_ct_a, v_comp_complex

def update_regulator_tap(net, reg_info, new_tap):
    """Update a regulator transformer's tap position by modifying vn_hv_kv."""
    trafo_idx = reg_info['trafo_idx']
    hv_kv = reg_info['hv_kv']
    ratio = 1.0 + new_tap * TAP_STEP
    new_vn_hv = hv_kv / ratio
    net.trafo.at[trafo_idx, 'vn_hv_kv'] = new_vn_hv
    return ratio

# ============================================================
# LDC ITERATIVE ALGORITHM
# ============================================================
print("\n" + "="*70)
print("INDEPENDENT LDC REGULATOR ALGORITHM")
print("="*70)

print("\n--- Regulator Excel Settings ---")
print(f"{'Reg':<8} {'From':>5} {'To':>5} {'Conn':<10} {'PT':>5} {'CT':>5} {'SetV':>5} {'CompR':>6} {'CompX':>6}")
print("-"*65)
for rg in regs:
    print(f"{rg['name']:<8} {rg['from']:>5} {rg['to']:>5} {rg['conn']:<10} {rg['pt']:>5.0f} {rg['ct']:>5.0f} {rg['set_v']:>5.0f} {rg['comp_r']:>6.1f} {rg['comp_x']:>6.1f}")

print(f"\nAlgorithm parameters:")
print(f"  Tap step size: {TAP_STEP*100:.3f}% = {TAP_STEP}")
print(f"  Tap range: ±{TAP_MAX} steps (ratio {1-TAP_MAX*TAP_STEP:.4f} to {1+TAP_MAX*TAP_STEP:.4f})")
print(f"  Bandwidth: {BANDWIDTH_V}V")
print(f"  Max iterations: {MAX_ITER}")
print(f"  CT secondary: {CT_SECONDARY_A}A")

# Step 1: Build network with tap=0 for all regulators
print("\n--- Step 1: Building network with neutral taps (tap=0) ---")
initial_taps = {rg['name']: 0.0 for rg in regs}
net, bd, reg_info = build_network(initial_taps)

# Run initial power flow
converged = run_pf(net)
if not converged:
    print("ERROR: Initial power flow did not converge!")
    sys.exit(1)
print("Initial power flow CONVERGED")

# Show initial voltages at regulator output buses
print("\n--- Initial regulator output bus voltages (tap=0) ---")
for ri in reg_info:
    v_out = net.res_bus.vm_pu.iloc[bd[ri['to']]]
    print(f"  {ri['name']}: bus {ri['to']} = {v_out:.4f} pu ({ri['lv_kv']:.2f} kV base)")

# Step 2: Iterative LDC tap adjustment
print(f"\n--- Step 2: Iterative LDC tap adjustment ---")
current_taps = {rg['name']: 0.0 for rg in regs}
previous_taps = {rg['name']: 0.0 for rg in regs}
reg_iterations = {rg['name']: 0 for rg in regs}
reg_final_status = {rg['name']: '' for rg in regs}

# Save initial network state
import copy, pandapower as pp
net_backup = pp.to_json(net)

for iteration in range(MAX_ITER):
    all_converged = True
    previous_taps = dict(current_taps)
    
    for ri in reg_info:
        name = ri['name']
        set_v = ri['set_v']
        
        # Compute compensated voltage (normalized to 120V base)
        v_comp, v_pt, i_ct, v_comp_cplx = compute_ldc_voltage(net, ri, bd)
        
        # Determine tap adjustment
        error = v_comp - set_v
        
        # Start with current tap (no change unless deadband exceeded)
        new_tap = current_taps[name]
        
        if abs(error) <= BANDWIDTH_V / 2:
            pass  # Within deadband - no change
        elif error < -BANDWIDTH_V / 2:
            # Compensated voltage too low - raise tap to boost voltage
            new_tap = current_taps[name] + 1
            all_converged = False
        else:
            # Compensated voltage too high - lower tap to reduce voltage
            new_tap = current_taps[name] - 1
            all_converged = False
        
        # Enforce tap limits
        new_tap = max(-TAP_MAX, min(TAP_MAX, new_tap))
        
        if new_tap != current_taps[name]:
            current_taps[name] = new_tap
            reg_iterations[name] += 1
            update_regulator_tap(net, ri, new_tap)
    
    # Print iteration summary
    taps_str = ", ".join([f"{n}={current_taps[n]:.0f}" for n in current_taps])
    print(f"  Iter {iteration+1:2d}: taps=[{taps_str}]", end="")
    
    # Re-run power flow
    converged = run_pf(net)
    if not converged:
        print(f" -> PF DIVERGED! Reverting taps.")
        # Revert all taps to previous state
        current_taps = dict(previous_taps)
        for ri in reg_info:
            update_regulator_tap(net, ri, current_taps[ri['name']])
        # Re-run with reverted taps
        converged = run_pf(net)
        if not converged:
            print("  ERROR: Cannot recover from divergence!")
        break
    
    if all_converged:
        print(f" -> ALL CONVERGED!")
        break
    
    if iteration == MAX_ITER - 1:
        print(f" -> MAX ITERATIONS")

# Mark regulators that hit tap limits
for ri in reg_info:
    name = ri['name']
    if current_taps[name] >= TAP_MAX:
        reg_final_status[name] = 'HIT_MAX'
    elif current_taps[name] <= -TAP_MAX:
        reg_final_status[name] = 'HIT_MIN'
    else:
        reg_final_status[name] = 'CONVERGED'

# ============================================================
# REGULATOR DEBUG OUTPUT
# ============================================================
print("\n" + "="*70)
print("REGULATOR DEBUG OUTPUT")
print("="*70)

for ri in reg_info:
    name = ri['name']
    set_v = ri['set_v']
    pt = ri['pt']
    ct_rating = ri['ct']
    comp_r = ri['comp_r']
    comp_x = ri['comp_x']
    step = TAP_STEP
    
    # Get final results
    v_comp, v_pt, i_ct, v_comp_cplx = compute_ldc_voltage(net, ri, bd)
    tap = current_taps[name]
    ratio = 1.0 + tap * step
    
    # Reference TXT tap (for comparison only - NOT used in model)
    ref_taps = {'Reg 1': 7.7, 'Reg 2': 12.7, 'Reg 3': 5.1, 'Reg 4': 3.0, 'Reg 5': -5.8}
    ref_tap = ref_taps.get(name, None)
    
    v_out_pu = net.res_bus.vm_pu.iloc[bd[ri['to']]]
    v_out_kv = v_out_pu * ri['lv_kv']
    
    # Target voltage in volts on 120V base
    target_v = set_v
    
    print(f"\n{'='*50}")
    print(f"Regulator: {name}")
    print(f"  Input bus:         {ri['from']}")
    print(f"  Output bus:        {ri['to']}")
    print(f"  Connection:        {ri['conn']}")
    print(f"  Phases:            {ri['phases']}")
    print(f"  SetV (120V base):  {set_v:.1f} V")
    print(f"  PT ratio:          {pt:.0f}")
    print(f"  CT rating:         {ct_rating:.0f} A")
    print(f"  CompR:             {comp_r:.1f} ohms")
    print(f"  CompX:             {comp_x:.1f} ohms")
    print(f"  Tap step:          {step*100:.3f}%")
    print(f"  Initial tap:       0.00")
    print(f"  Calculated tap:    {tap:.1f}")
    print(f"  Reference TXT tap: {ref_tap:.1f}" if ref_tap is not None else "  Reference TXT tap: N/A")
    print(f"  Difference:        {tap - ref_tap:+.1f}" if ref_tap is not None else "  Difference:        N/A")
    print(f"  Tap ratio:         {ratio:.4f}")
    print(f"  Final V_out:       {v_out_pu:.4f} pu ({v_out_kv:.2f} kV)")
    print(f"  V_pt (PT sec):     {v_pt:.2f} V (on {pt:.0f}V base)")
    print(f"  V_comp (120V base):{v_comp:.2f} V")
    print(f"  Target voltage:    {target_v:.2f} V (120V base)")
    print(f"  V_comp error:      {v_comp - set_v:+.2f} V")
    print(f"  Iterations:        {reg_iterations[name]}")
    print(f"  Convergence:       {reg_final_status[name]}")

# ============================================================
# FINAL POWER FLOW AND RESULTS
# ============================================================
print("\n" + "="*70)
print("FINAL POWER FLOW RESULTS (INDEPENDENT LDC TAPS)")
print("="*70)

print("\n--- Bus Voltages ---")
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

# Save network
try:
    pp.to_json(net, r'C:\Users\ASUS\Documents\suryaghar\feeder_network_ldc.json')
    print("\nNetwork saved to feeder_network_ldc.json")
except: pass

# ============================================================
# SAVE TAP SUMMARY FOR COMPARISON
# ============================================================
print("\n" + "="*70)
print("TAP SUMMARY: INDEPENDENT CALCULATION vs TXT REFERENCE")
print("="*70)
print(f"\n{'Reg':<8} {'Calc Tap':>10} {'Ref Tap':>10} {'Diff':>8} {'Status':<12}")
print("-"*55)
for ri in reg_info:
    name = ri['name']
    calc_tap = current_taps[name]
    ref_tap = ref_taps.get(name, None)
    if ref_tap is not None:
        diff = calc_tap - ref_tap
        print(f"{name:<8} {calc_tap:>10.1f} {ref_tap:>10.1f} {diff:>+8.1f} {reg_final_status[name]:<12}")
    else:
        print(f"{name:<8} {calc_tap:>10.1f} {'N/A':>10} {'N/A':>8} {reg_final_status[name]:<12}")

print("\nDone.")
