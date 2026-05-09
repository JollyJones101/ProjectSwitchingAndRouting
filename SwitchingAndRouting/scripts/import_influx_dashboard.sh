#!/usr/bin/env bash
# Import an InfluxDB v2 dashboard JSON into the running InfluxDB instance.
# Usage: ./scripts/import_influx_dashboard.sh ./docker/influxdb/sensor_dashboard.json

set -euo pipefail

JSON_FILE=${1:-./docker/influxdb/sensor_dashboard.json}
INFLUX_URL=${INFLUX_URL:-http://localhost:8086}
TOKEN=${DOCKER_INFLUXDB_INIT_ADMIN_TOKEN:-supersecrettoken}

if [ ! -f "$JSON_FILE" ]; then
  echo "Dashboard file not found: $JSON_FILE"
  exit 1
fi

echo "Waiting for InfluxDB to become available at $INFLUX_URL..."
until curl -sSf "$INFLUX_URL/health" >/dev/null; do
  sleep 2
done

echo "Importing dashboard $JSON_FILE"
curl -sS -X POST "$INFLUX_URL/api/v2/dashboards" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  --data-binary @"$JSON_FILE" || {
    echo "Import failed" >&2
    exit 2
}

echo "Import complete."
