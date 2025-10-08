#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
plot_courant.py
Estrae "Courant Number mean/max" dal log e li plotta vs tempo.
Uso:
  python plot_courant.py --log solver.log --out courant_vs_time.png
"""
import re, argparse
from pathlib import Path
import matplotlib.pyplot as plt

def parse_courant(log_path: Path):
    time_re = re.compile(r"^\s*Time\s*=\s*([0-9eE+\-\.]+)\s*$")
    co_re   = re.compile(r"^\s*Courant Number mean:\s*([0-9eE+\-\.]+)\s*max:\s*([0-9eE+\-\.]+)\s*$")
    t, co_m, co_M = [], [], []
    t_now = None
    with log_path.open("r", errors="ignore") as f:
        for line in f:
            m = time_re.match(line)
            if m:
                t_now = float(m.group(1)); continue
            m = co_re.match(line)
            if m and t_now is not None:
                t.append(t_now)
                co_m.append(float(m.group(1)))
                co_M.append(float(m.group(2)))
    return t, co_m, co_M

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    ap.add_argument("--out", default="courant_vs_time.png")
    args = ap.parse_args()

    t, m, M = parse_courant(Path(args.log))
    if not t:
        raise SystemExit("Nessun dato trovato. Assicurati di aver rediretto il solver in un log.")

    plt.figure()
    plt.plot(t, m, label="CO mean")
    plt.plot(t, M, label="CO max")
    plt.xlabel("Time [s]"); plt.ylabel("Courant [-]")
    plt.title("Courant vs Time"); plt.grid(True); plt.legend(); plt.tight_layout()
    plt.savefig(args.out, dpi=200)
    print(f"✔ Salvato: {args.out}")

