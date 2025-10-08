#!/bin/bash

# File e directory da conservare
KEEP_FILES=("Solid.inp" "config.yml" "clean.sh")
KEEP_DIRS=("ccxToParaview")

# Vai nella directory dello script
cd "$(dirname "$0")" || { echo "Errore: impossibile accedere alla directory."; exit 1; }

# Cicla su tutto il contenuto della cartella corrente
for item in *; do
  KEEP=false

  # Verifica se è un file da mantenere
  for keep in "${KEEP_FILES[@]}"; do
    if [ "$item" == "$keep" ]; then
      KEEP=true
      break
    fi
  done

  # Verifica se è una directory da mantenere
  if [ -d "$item" ]; then
    for keep in "${KEEP_DIRS[@]}"; do
      if [ "$item" == "$keep" ]; then
        KEEP=true
        break
      fi
    done
  fi

  # Se non è da mantenere, lo rimuove
  if [ "$KEEP" == false ]; then
    echo "Rimuovo: $item"
    rm -rf "$item"
  fi
done

echo "Pulizia completata. File e cartelle mantenuti: ${KEEP_FILES[*]} ${KEEP_DIRS[*]}"

