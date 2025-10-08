# fit_HF_views.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

DATA_PATH = Path("postProcessing/qIn_BroodHole/0/surfaceFieldValue.dat")
OUT_FILE = "HF_views.png"

def read_surface_field_value(path: Path):
    """Legge 2 colonne: Time   areaIntegrate(wallHeatFlux)"""
    t, q = [], []
    with path.open("r", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            try:
                tt = float(parts[0])
                qq = float(parts[1])
            except ValueError:
                continue
            t.append(tt); q.append(qq)
    t = np.array(t, dtype=float)
    q = np.array(q, dtype=float)
    idx = np.argsort(t)
    return t[idx], q[idx]

def smooth_interp(t, y, n=300):
    """Interpolazione lineare semplice."""
    if t.size < 2:
        return t, y
    t_dense = np.linspace(t.min(), t.max(), n)
    y_dense = np.interp(t_dense, t, y)
    return t_dense, y_dense

if __name__ == "__main__":
    if not DATA_PATH.exists():
        raise SystemExit(f"File non trovato: {DATA_PATH}")

    t, q = read_surface_field_value(DATA_PATH)
    if t.size == 0:
        raise SystemExit("Nessun dato valido letto dal file.")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # ---- Subplot 1: semilogy ----
    td, qd = smooth_interp(t, q)
    ax1.semilogy(t, q, 'o', color="blue", markersize=3, label="dati")
    ax1.semilogy(td, qd, '-', color="skyblue", linewidth=1.0)  # senza label
    ax1.set_xlabel("Time [s]")
    ax1.set_ylabel(r"$\dot{Q}$  [W]")
    ax1.set_title("Heat flux (semilogy)")
    ax1.grid(True, which="both", linestyle="--", alpha=0.4)
    ax1.legend()

    # ---- Subplot 2: q vs 1/sqrt(t) ----
    mask_pos = t > 0.0
    t_pos = t[mask_pos]; q_pos = q[mask_pos]
    if t_pos.size >= 2:
        invsqrt_t = 1.0 / np.sqrt(t_pos)
        idx2 = np.argsort(invsqrt_t)
        x = invsqrt_t[idx2]; y = q_pos[idx2]
        xd, yd = smooth_interp(x, y)
        ax2.plot(x, y, 'o', color="blue", markersize=3, label="dati")
        ax2.plot(xd, yd, '-', color="skyblue", linewidth=1.0)  # senza label
        ax2.set_xlabel(r"$1/\sqrt{t}$  [s$^{-1/2}$]")
        ax2.set_ylabel(r"$\dot{Q}$  [W]")
        ax2.set_title(r"Heat flux vs $1/\sqrt{t}$")
        ax2.grid(True, linestyle="--", alpha=0.4)
        ax2.legend()

    plt.tight_layout()
    plt.savefig(OUT_FILE, dpi=200)
    print(f"✔ Salvato: {OUT_FILE}")

