"""
Diagnostic: try building network in stages to find convergence blocker
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
            v = [sf(ws.cell_value(ri,c)) for c in range(1, min(11, ws.ncols))]
            while len(v)<10: v.append(0)
            zb[i] = [complex(v[0],v[1]),complex(v[2],v[3]),complex(v[4],v[5])]
        cfg_z[lbl] = zb; r+=4; continue
    cn = sf(cv)
    if cn == 0: r+=1; continue
    zb = np.zeros((3,3), dtype=complex)
    for i in range(3):
        ri = r+i
        if ri >= ws.nrows: break
        v = [sf(ws.cell_value(ri,c)) for c in range(1, min(11, ws.ncols))]
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
for row in range(7, ws.nrows):
    n = ws.cell_value(row, 0)
    if n == '' or n is None: continue
    lines_data.append({
        'name': str(n).strip(), 'from': str(ws.cell_value(row,1)).strip(),
        'to': str(ws.cell_value(row,2)).strip(),
        'config': si(ws.cell_value(row,3)),
        'length': sf(ws.cell_value(row,4)),
    })

# Construction Code / conductor mapping
ws_cc = wb.sheet_by_name('Construction Code')
cc_map = {}
for row in range(3, ws_cc.nrows):
    cn = ws_cc.cell_value(row, 0)
    if cn == '' or cn is None: continue
    cfg_code = si(ws_cc.cell_value(row, 1))
    phase = str(ws_cc.cell_value(row, 2)).strip()
    cond = str(ws_cc.cell_value(row, 3)).strip()
    cc_map[str(cn).strip()] = {'config': cfg_code, 'phase': phase, 'conductor': cond}

# Conductor Data - Get per-mile impedances
ws_cd = wb.sheet_by_name('Conductor Data')
cond_data = {}
for row in range(4, ws_cd.nrows):
    cn = ws_cd.cell_value(row, 0)
    if cn == '' or cn is None: continue
    cond_data[str(cn).strip()] = {
        'r1': sf(ws_cd.cell_value(row, 1)),
        'x1': sf(ws_cd.cell_value(row, 2)),
    }

# Lines: compute per-km impedances
print("=== LINE IMPEDANCES ===")
for ln in lines_data:
    cc_name = ln['name']  # Lines use construction code name as line name
    if cc_name in cc_map:
        config = cc_map[cc_name]['config']
        z = get_config_z(config)
        if z is not None:
            a = np.exp(1j * 2 * np.pi / 3)
            A = np.array([[1,1,1],[1,a**2,a],[1,a,a**2]])
            Z012 = np.linalg.inv(A) @ z @ A
            Z1 = Z012[1,1]
            # Convert to per-km (divide by length in miles, multiply by 0.001 for km)
            length_km = ln['length']
            if length_km > 0:
                r_per_km = Z1.real / (length_km * 1.60934) * 1000  # ohm/km
                x_per_km = Z1.imag / (length_km * 1.60934) * 1000
            else:
                r_per_km = 0; x_per_km = 0
            print(f"  {ln['name']:>12s}: config={config}, L={length_km:.2f}mi, Z1={Z1:.4f} ohm/mi, "
                  f"R={r_per_km:.4f} ohm/km, X={x_per_km:.4f} ohm/km")
        else:
            print(f"  {ln['name']:>12s}: config {config} NOT FOUND")
    else:
        print(f"  {ln['name']:>12s}: construction code not found")

# Now check voltage levels at each bus
print("\n=== BUS VOLTAGE LEVELS ===")
# Re-read to get node info
ws = wb.sheet_by_name('Lines')
all_nodes = set()
bus_vn = {}
for row in range(7, ws.nrows):
    n = ws.cell_value(row, 0)
    if n == '' or n is None: continue
    fr = str(ws.cell_value(row,1)).strip()
    to = str(ws.cell_value(row,2)).strip()
    all_nodes.add(fr); all_nodes.add(to)
    # Need to get voltage levels...
# Actually let me just print the lines data with lengths
print(f"Total lines: {len(lines_data)}")
print(f"Total nodes in lines: {len(all_nodes)}")

# Check xfm Z data for zero impedance transformers
print("\n=== XFM Z DATA ===")
ws = wb.sheet_by_name('Xfm Z')
for row in range(4, ws.nrows):
    n = ws.cell_value(row, 0)
    if n == '' or n is None: continue
    r_val = sf(ws.cell_value(row, 1))
    x_val = sf(ws.cell_value(row, 2))
    if r_val == 0 and x_val == 0:
        print(f"  WARNING: {n} has R=0, X=0!")

# Check for zero-length lines
print("\n=== ZERO/SHORT LENGTH LINES ===")
for ln in lines_data:
    if ln['length'] <= 0.01:
        print(f"  {ln['name']:>12s}: length={ln['length']} mi, from={ln['from']}, to={ln['to']}")

print("\nDone.")
