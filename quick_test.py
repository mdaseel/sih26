"""Quick diagnostic: check transformer mismatches and test convergence"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandapower as pp
import pandas as pd
import numpy as np
import xlrd
import math
import warnings
warnings.filterwarnings('ignore')

# ====== Paste key functions from build_feeder.py ======
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

xls_path = r"C:\Users\ASUS\Documents\suryaghar\IEEE-Comp-Test-Feeder-Data-20140401.xls"
wb = xlrd.open_workbook(xls_path)

# Source
ws = wb.sheet_by_name('Source')
source_kV = sf(ws.cell_value(3, 0))

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
        zb = np.zeros((3,3), dtype=complex)
        for i in range(3):
            ri = r+i
            if ri >= ws.nrows: break
            v = [sf(ws.cell_value(ri,c)) for c in range(1,min(11,ws.ncols))]
            while len(v)<10: v.append(0)
            zb[i] = [complex(v[0],v[1]),complex(v[2],v[3]),complex(v[4],v[5])]
        cfg_z[lbl] = zb; r+=4; continue
    cn = sf(cv)
    if cn == 0: r+=1; continue
    zb = np.zeros((3,3), dtype=complex)
    for i in range(3):
        ri = r+i
        if ri >= ws.nrows: break
        v = [sf(ws.cell_value(ri,c)) for c in range(1,min(11,ws.ncols))]
        while len(v)<10: v.append(0)
        zb[i] = [complex(v[0],v[1]),complex(v[2],v[3]),complex(v[4],v[5])]
    cfg_z[int(cn)] = zb; r+=4

def get_config_z(cc):
    if cc in cfg_z: return cfg_z[cc]
    ks = f"{cc} self"
    if ks in cfg_z: return cfg_z[ks]
    return None

# Lines
ws = wb.sheet_by_name('Lines')
lines_data = []
for r in range(2, ws.nrows):
    nm = ws.cell_value(r,0)
    if not nm: continue
    lines_data.append({'name':nm, 'from':si(ws.cell_value(r,1)), 'to':si(ws.cell_value(r,2)),
                       'length_ft':sf(ws.cell_value(r,3)), 'config':si(ws.cell_value(r,9))})

# Build a MINIMAL network - just ext_grid, T-SUB, main feeder lines, regulators, loads
# No LV transformers, no distribution transformers
net = pp.create_empty_network(name="Test", f_hz=60)

# Bus 700 = 115 kV
b700 = pp.create_bus(net, vn_kv=115.0, name="700")
b701 = pp.create_bus(net, vn_kv=24.9, name="701")
pp.create_ext_grid(net, bus=b700, vm_pu=1.0, va_degree=0.0)

# T-SUB
sub_vk = math.sqrt(sub['X']**2 - sub['R']**2)
pp.create_transformer_from_parameters(
    net, hv_bus=b700, lv_bus=b701,
    sn_mva=sub['kVA']/1000, vn_hv_kv=115.0, vn_lv_kv=24.9,
    vkr_percent=sub['R'], vk_percent=sub['X'],
    pfe_kw=0, i0_percent=0, name="T-SUB", vector_group="YNd11")

# Add just the main feeder lines (non-zero length, config 400)
for l in lines_data:
    if l['length_ft'] <= 0: continue  # Skip zero-length
    cc = l['config']
    Z = get_config_z(cc)
    if Z is None: continue
    Z012 = sym_seq_Z(Z)
    Z1 = Z012[1,1]
    r_km = Z1.real / 1.60934
    x_km = Z1.imag / 1.60934
    lkm = l['length_ft'] / 5280.0 * 1.60934
    if lkm < 0.01: continue  # Skip very short lines
    
    fr, to = l['from'], l['to']
    # Only add if both buses are 24.9 kV main feeder
    main_24 = {701,702,703,704,713,717,718,719,727,729,731,735,736,737,738,
               741,742,744,745,746,747,749,750,752,753,757,758,760,761,763,
               765,771}
    if fr not in main_24 or to not in main_24:
        continue
    
    # Create buses as needed
    if fr not in [b.name for b in net.bus.values]:
        pass  # skip
    if to not in [b.name for b in net.bus.values]:
        pass  # skip
    
    print(f'  Line {l[\"name\"]}: {fr}->{to}, config={cc}, L={lkm:.4f}km, R={r_km:.4f}, X={x_km:.4f}')

print(f'Net so far: {len(net.bus)} buses, {len(net.line)} lines, {len(net.trafo)} trafos')
print('Test done - just checking data reads')
