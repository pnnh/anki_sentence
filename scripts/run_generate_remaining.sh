#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.."
mkdir -p logs

SCENES=(
  cafe_fastfood
  online_shopping
  public_transport
  phone_internet
  courier
  hair_salon
  renting_repair
  car_parking
  emergencies
  office
  school
  phone_service
  socializing
  sightseeing
  weather_smalltalk
)

for s in "${SCENES[@]}"; do
  echo "===== $(date '+%F %T') PLAN $s ====="
  python3 scripts/plan.py --scene "$s" --items 10
  python3 scripts/clean_plans.py "data/plans/$s.json" --apply
  echo "===== $(date '+%F %T') GENERATE $s ====="
  python3 scripts/generate.py --scene "$s" --pause 2
  echo "===== $(date '+%F %T') SLEEP 90s ====="
  sleep 90
done

echo "===== $(date '+%F %T') REMAINING GENERATION DONE ====="
