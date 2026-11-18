#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.."
mkdir -p logs

SCENES=(
  shopping_clothes
  supermarket
  restaurant
  food_delivery
  taxi
  airport
  hotel
  directions
  doctor_pharmacy
  banking
)

for s in "${SCENES[@]}"; do
  echo "===== $(date '+%F %T') GENERATE $s ====="
  python3 scripts/generate.py --scene "$s" --pause 2
  echo "===== $(date '+%F %T') SLEEP 90s ====="
  sleep 90
done

echo "===== $(date '+%F %T') CORE GENERATION DONE ====="
