#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bees_vs_BroodHole.py
Crea due figure:
  1) beesQdot_vs_BroodHoleEnergy.png  -> Q_BroodHole(t) [J] (rosso, asse sinistro) + dot{Q}_bees [W] (nero, asse destro)
  2) beesEnergy_vs_BroodHoleEnergy.png -> DUE PANNELLI:
       (sopra)  Q_bees(t) [J]  in nero con la propria scala
       (sotto)  Q_Brood(t) [J] in rosso con la propria scala

  Uso:
  python3 bees_vs_BroodHole.py
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
    k = round(t/base)
    return abs(t - k*base) <= tol

def filter_full_steps(times, values, base=0.1, tol=5e-3):
    mask = np.array([is_multiple_of(tt, base, tol) for tt in times])
    times = times[mask]; values = values[mask]
    idx = np.argsort(times)
    return times[idx], values[idx]

def cumulative_trapz(t, y):
    if len(t) < 2:
        return np.zeros_like(t)
    Q = np.zeros_like(t)
    for i in range(1, len(t)):
        dt = t[i] - t[i-1]
        Q[i] = Q[i-1] + 0.5*(y[i]+y[i-1])*dt
    return Q

def find_default_dat(base_dir: Path) -> Path | None:
    if not base_dir.exists():
        return None
    time_dirs = []
    for p in base_dir.iterdir():
        if p.is_dir():
            try:
                time_dirs.append((float(p.name), p))
            except ValueError:
                pass
    if not time_dirs:
        return None
    latest_dir = sorted(time_dirs, key=lambda x: x[0])[-1][1]
    for c in (latest_dir / "surfaceFieldValue.dat",
              latest_dir / "surfaceFieldsValue.dat"):
        if c.exists():
            return c
    return None

def crossings_linear_interp(t, y, yref):
    t = np.asarray(t); y = np.asarray(y)
    if np.isscalar(yref):
        yref = np.full_like(y, float(yref))
    else:
        yref = np.asarray(yref)
        assert yref.shape == y.shape
    diff = y - yref
    xs, ys = [], []
    for k in range(1, len(t)):
        if diff[k] == 0:
            xs.append(t[k]); ys.append(y[k])
        elif diff[k-1] == 0:
            xs.append(t[k-1]); ys.append(y[k-1])
        elif diff[k]*diff[k-1] < 0:
            t1, t2 = t[k-1], t[k]
            d1, d2 = diff[k-1], diff[k]
            if (d2 - d1) != 0:
                tc = t1 - d1*(t2 - t1)/(d2 - d1)
            else:
                tc = 0.5*(t1+t2)
            yr = yref[k-1] + (yref[k]-yref[k-1])*(tc - t1)/(t2 - t1)
            xs.append(tc); ys.append(yr)
    return xs, ys

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="postProcessing/qIn_BroodHole")
    ap.add_argument("--file", default=None)
    ap.add_argument("--out1", default="beesQdot_vs_BroodHoleEnergy.png")
    ap.add_argument("--out2", default="beesEnergy_vs_BroodHoleEnergy.png")
    ap.add_argument("--stepBase", type=float, default=0.1)
    ap.add_argument("--tol", type=float, default=5e-3)
    ap.add_argument("--beesPower", type=float, default=4.8,
                    help="Valore di dot{Q}_bees in W")
    args = ap.parse_args()

    if args.file:
        path = Path(args.file)
    else:
        path = find_default_dat(Path(args.dir))
    if not path or not Path(path).exists():
        raise SystemExit("❌ File non trovato.")

    print(f"✓ Leggo: {path}")
    t_raw, qdot_raw = read_surface_fields(path)
    tt, qq = filter_full_steps(t_raw, qdot_raw, base=args.stepBase, tol=args.tol)
    if tt.size == 0:
        raise SystemExit("❌ Nessun tempo pieno trovato.")
    t_rel = tt - tt[0]

    Q_brood = cumulative_trapz(tt, qq)
    qdot_bees = float(args.beesPower)
    Q_bees = qdot_bees * t_rel

    xE, yE = crossings_linear_interp(tt, Q_brood, Q_bees)

    # ---- FIGURA 1 ----
    fig1, ax1 = plt.subplots(figsize=(10, 5.8))
    l1, = ax1.plot(tt, Q_brood, color="red", lw=1.8,
                   label=r"$Q_\mathrm{Brood}(t)$ [J]")
    ax1.set_xlabel("Time [s]")
    ax1.set_ylabel("Energy [J]", color="red")
    ax1.tick_params(axis="y", labelcolor="red")
    ax1.grid(True, alpha=0.25)

    ax1r = ax1.twinx()
    l2 = ax1r.axhline(qdot_bees, color="black", lw=1.8,
                      label=fr"$\dot{{Q}}_\mathrm{{bees}}={qdot_bees:.2f}\,\mathrm{{W}}$")
    ax1r.set_ylabel(r" $\dot{Q}$ [W]", color="black")
    ax1r.tick_params(axis="y", labelcolor="black")

    lines = [l1, l2]
    labels = [ln.get_label() for ln in lines]
    ax1.legend(lines, labels, loc="best")
    ax1.set_title(r"Calore disperso ($Q_\mathrm{Brood}(t)$) vs Potenza generata ($\dot{Q}_\mathrm{bees}$)")

    fig1.tight_layout()
    fig1.savefig(args.out1, dpi=220)
    print(f"✔ Salvato: {Path(args.out1).resolve()}")

    # ---- FIGURA 2: due pannelli (Q_bees sopra, Q_brood sotto) ----
    fig2, (ax_top, ax_bot) = plt.subplots(
        nrows=2, ncols=1, sharex=True, figsize=(10, 7.2),
        gridspec_kw={"height_ratios": [1, 1], "hspace": 0.15}
    )

    # Pannello superiore: Q_bees(t) [J] in nero
    ax_top.plot(tt, Q_bees, color="black", lw=1.8,
                label=r"$Q_\mathrm{bees}(t)=\dot{Q}_\mathrm{bees}\,t$ [J]")
    for tc, _ in zip(xE, yE):
        ax_top.axvline(tc, color="#7f7f7f", ls=":", lw=1.0)
    ax_top.set_ylabel("Energy [J]", color="black")
    ax_top.tick_params(axis="y", labelcolor="black")
    ax_top.grid(True, alpha=0.25)
    ax_top.legend(loc="best")
    ax_top.set_title(r"Calore generato $Q_\mathrm{bees}(t)$) vs Calore disperso $Q_\mathrm{Brood}(t)$")

    # Pannello inferiore: Q_Brood(t) [J] in rosso
    ax_bot.plot(tt, Q_brood, color="red", lw=1.8,
                label=r"$Q_\mathrm{Brood}(t)$ [J]")
    for tc, _ in zip(xE, yE):
        ax_bot.axvline(tc, color="#7f7f7f", ls=":", lw=1.0)
    ax_bot.set_xlabel("Time [s]")
    ax_bot.set_ylabel("Energy [J]", color="red")
    ax_bot.tick_params(axis="y", labelcolor="red")
    ax_bot.grid(True, alpha=0.25)
    ax_bot.legend(loc="best")

    fig2.tight_layout()
    fig2.savefig(args.out2, dpi=220)
    print(f"✔ Salvato: {Path(args.out2).resolve()}")

