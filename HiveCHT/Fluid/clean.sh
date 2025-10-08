#!/bin/bash

# Cartelle da conservare
KEEP_DIRS=("0" "constant" "system")

# Cancella tutte le directory tranne quelle da conservare
for item in *; do
  if [ -d "$item" ]; then
    KEEP=false
    for keep in "${KEEP_DIRS[@]}"; do
      if [ "$item" == "$keep" ]; then
        KEEP=true
        break
      fi
    done

    if [ "$KEEP" == false ]; then
      echo "Rimuovo la cartella: $item"
      rm -rf "$item"
    fi
  fi
done

# Cancella tutti i file .log nella directory corrente
echo "Rimuovo file *.log"
rm -f *.log

echo "Pulizia completata. Cartelle rimaste: ${KEEP_DIRS[*]}"

