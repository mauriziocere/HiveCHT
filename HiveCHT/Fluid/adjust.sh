#!/bin/bash
# clean_timesteps.sh
# Cancella directory timestep con due decimali "non pieni" (es: 0.09, 1.19, ecc.)
# Mantiene cartelle con tempi "pieni" (0.1, 0.2, 1.0, ecc.) e tutto il resto.

shopt -s extglob

for d in */ ; do
  # togli lo slash finale
  d="${d%/}"

  # controlla che sia un numero
  if [[ "$d" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
    # è un numero (potenziale timestep)
    # estrai parte decimale
    if [[ "$d" == *.* ]]; then
      decimals="${d##*.}"
      # se ha due cifre decimali e NON termina per 0 (es. .09, .19, .29 ...)
      if [[ ${#decimals} -eq 1 && "${decimals:1:1}" != "0" ]]; then
        echo ">>> Cancello $d"
        rm -rf "$d"
      else
        echo ">>> Tengo $d"
      fi
    else
      # è un intero (0,1,2,...) → lo teniamo
      echo ">>> Tengo $d"
    fi
  else
    # non è numerico (tipo system, constant, postProcessing...) → lo teniamo
    echo ">>> Tengo $d"
  fi
done

