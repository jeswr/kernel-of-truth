"""Mock runner for a single cell: python run_one.py LABEL RHO R [n] [regime]

Writes a JSON report to results/mock/ and prints the human report.  MOCK ONLY
(small R); never the full grid.
"""
import sys
import os
import json
import grid
import driver

def main():
    label = sys.argv[1]
    rho = float(sys.argv[2])
    R = int(sys.argv[3])
    nlevel = sys.argv[4] if len(sys.argv) > 4 else 'base'
    regime = sys.argv[5] if len(sys.argv) > 5 else 'gaussian'
    idx, t = grid.cell_by_label(label, rho=rho, n=nlevel, regime=regime)
    want_paths = t.kind in ('power',) or label in ('P1', 'P2', 'P3', 'P4', 'P5', 'P6')
    out = driver.run_cell(idx, t, R=R, want_paths=want_paths, progress=True)
    driver.print_report(out)
    os.makedirs('results/mock', exist_ok=True)
    fn = f"results/mock/{label}_rho{rho}_{nlevel}_{regime}_R{R}.json"
    with open(fn, 'w') as f:
        json.dump(out, f, indent=2, default=str)
    print('wrote', fn)

if __name__ == '__main__':
    main()
