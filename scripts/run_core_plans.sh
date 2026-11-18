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
  echo "===== $(date '+%F %T') PLAN $s ====="
  python3 scripts/plan.py --scene "$s" --items 10
  echo "===== $(date '+%F %T') SLEEP 20s ====="
  sleep 20
done

echo "===== $(date '+%F %T') PLANS DONE ====="
