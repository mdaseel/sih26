"""Parse reference TXT and compare with pandapower results"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\Users\ASUS\Documents\suryaghar\IEEE_CompTestFeeder_Results_20140401.txt', 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

# Find bus voltage lines
print("=== Key Bus Voltages from Reference (Phase A) ===")
for target in [700, 701, 702, 703, 704, 713, 717, 727, 731, 735, 736, 741, 742, 744, 745, 746, 747, 749, 750, 752, 753]:
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(str(target) + ' ') and 'A' in stripped.split():
            parts = stripped.split()
            # Find phase A
            for j, p in enumerate(parts):
                if p == 'A' and j > 0 and j < 5:
                    # Get Pri kV
                    for k in range(j+2, min(j+6, len(parts))):
                        if 'Y' in parts[k] or 'D' in parts[k]:
                            pri_kv = parts[k]
                            break
                    else:
                        pri_kv = '?'
                    # Get Base Volt
                    for k in range(j+3, min(j+8, len(parts))):
                        try:
                            bv = float(parts[k])
                            if 90 < bv < 130:
                                base_v = bv
                                break
                        except:
                            continue
                    else:
                        base_v = 0
                    print(f"  Bus {target:>4d}: {pri_kv:>10s}  base={base_v:.1f}V")
                    break
            break

# Find transformer loading lines
print("\n=== Transformer Reference Data ===")
for target in ['T-SUB', 'T1', 'T3', 'T4', 'T7', 'T8', 'T11', 'T22', 'T24',
               'T5', 'T6', 'T13', 'T14', 'T19', 'T2', 'T12', 'T16', 'T17', 'T18', 'T23',
               'T9', 'T10', 'T15', 'T20', 'T21']:
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(target + ' ') or stripped.startswith(target + '\t'):
            parts = stripped.split()
            if len(parts) >= 8 and parts[2] == 'A':
                print(f"  {stripped[:140]}")
                break
