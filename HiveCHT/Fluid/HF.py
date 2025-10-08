#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HF.py — Plot della portata di calore istantanea \dot{Q}(t) [W] e del calore cumulato Q(t) [J]
         dai risultati di surfaceFieldValue.

Uso:
    python3 HF.py

Opzioni:(per cambiare eventualmente la patch di cui si vuole plottare HF e i tempi)
    --dir  postProcessing/qIn_BroodHole     (base dir; default)
    --file .../surfaceFieldValue.dat        (se vuoi puntare a un file preciso)
    --out  heat_vs_time.png                 (output nella cwd; default)
    --stepBase 0.1 --tol 0.005              (filtra solo “tempi pieni”)
"""

import argparse
from pathlib import Path
import re
import numpy as np
import matplotlib.pyplot as plt

def read_surface_fields(path: Path):
    times, qdot = [], []
    with path.open("r", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = re.split(r"\s+", line)
            if len(parts) < 2:
                continue
            try:
                t = float(parts[0]); v = float(parts[1])
            except ValueError:
                continue
            times.append(t); qdot.append(v)
    return np.array(times, dtype=float), np.array(qdot, dtype=float)

def is_multiple_of(t, base=0.1, tol=5e-3):
    if base <= 0:
        return True
    k = round(t/base)
    return abs(t - k*base) <= tol

def filter_full_steps(times, values, base=0.1, tol=5e-3):
    mask = np.array([is_multiple_of(tt, base, tol) for tt in times])
    return times[mask], values[mask]

def cumulative_trapz(t, y):
    if len(t) < 2:
        return np.zeros_like(t), t, y
    idx = np.argsort(t)
    t = t[idx]; y = y[idx]
    Q = np.zeros_like(t)
    for i in range(1, len(t)):
        dt = t[i] - t[i-1]
        Q[i] = Q[i-1] + 0.5*(y[i]+y[i-1])*dt
    return Q, t, y

def find_default_dat(base_dir: Path) -> Path | None:
    if not base_dir.exists():
        return None

    time_dirs = []
    for p in base_dir.iterdir():
        if p.is_dir():
            try:
                _ = float(p.name)
                time_dirs.append((float(p.name), p))
            except ValueError:
                pass
    if not time_dirs:
        return None

    time_dirs.sort(key=lambda x: x[0])   # crescente
    latest_dir = time_dirs[-1][1]

    candidates = [
        latest_dir / "surfaceFieldValue.dat",
        latest_dir / "surfaceFieldsValue.dat",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="postProcessing/qIn_BroodHole",
                    help="Directory base del postProcessing (default: postProcessing/qIn_BroodHole)")
    ap.add_argument("--file", default=None,
                    help="Percorso esplicito del file surfaceFieldValue(s).dat (override di --dir)")
    ap.add_argument("--out", default="heat_vs_time.png",
                    help="PNG di output (salvato nella cartella corrente)")
    ap.add_argument("--stepBase", type=float, default=0.1,
                    help="Intervallo dei 'tempi pieni' (default 0.1 s)")
    ap.add_argument("--tol", type=float, default=5e-3,
                    help="Tolleranza matching tempi (default 0.005 s)")
    args = ap.parse_args()

    if args.file:
        path = Path(args.file)
    else:
        path = find_default_dat(Path(args.dir))

    if not path or not Path(path).exists():
        raise SystemExit(
            "❌ File non trovato.\n"
            "  - Controlla che esista qualcosa in postProcessing/qIn_BroodHole/<tempo>/surfaceFieldValue(s).dat\n"
            "  - In alternativa passa --file PATH_COMPLETO al .dat"
        )

    print(f"✓ Leggo: {path}")
    t, qdot = read_surface_fields(Path(path))
    if t.size == 0:
        raise SystemExit("❌ Nessun dato leggibile nel file selezionato.")

    tf, qf = filter_full_steps(t, qdot, base=args.stepBase, tol=args.tol)
    if tf.size == 0:
        raise SystemExit("❌ Nessun 'tempo pieno' individuato. Aumenta --tol o verifica lo stepBase.")

    Qcum, tt, qq = cumulative_trapz(tf, qf)

    # --- figura con doppia scala ---
    fig, ax_left = plt.subplots(figsize=(10, 5.8))

    # Asse sinistro: potenza \dot{Q}(t) [W] in nero
    l_pow, = ax_left.plot(tt, qq, color="black", lw=1.8,
                          label=r"$\dot{Q}(t)$ [W]  (Potenza dispersa)")
    ax_left.set_xlabel("Time [s]")
    ax_left.set_ylabel(r"$\dot{Q}(t)$ [W]", color="black")
    ax_left.tick_params(axis="y", labelcolor="black")
    ax_left.grid(True, alpha=0.25)

    # Asse destro: calore cumulato Q(t) [J] in rosso
    ax_right = ax_left.twinx()
    l_Q, = ax_right.plot(tt, Qcum, color="red", lw=1.8,
                         label=r"$Q(t)$ [J]  (Calore disperso al tempo t)")
    ax_right.set_ylabel(r"$Q(t)$ [J]", color="red")
    ax_right.tick_params(axis="y", labelcolor="red")

    # Legenda combinata
    lines = [l_pow, l_Q]
    labels = [ln.get_label() for ln in lines]
    ax_left.legend(lines, labels, loc="best")

    plt.title(r"Potenza ($\dot{Q}(t)$) e calore ($Q(t)$) dispersi da Brood")
    fig.tight_layout()
    fig.savefig(args.out, dpi=200)
    print(f"✔ Salvato: {Path(args.out).resolve()}")

