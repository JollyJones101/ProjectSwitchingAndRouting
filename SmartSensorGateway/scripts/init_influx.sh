#!/usr/bin/env bash
# Wait for InfluxDB to be available and create database 'sensordata'
set -e
INFLUX_HOST=${INFLUX_HOST:-http://localhost:8086}
DB_NAME=${DB_NAME:-sensordata}

echo "Waiting for InfluxDB at $INFLUX_HOST..."
for i in {1..30}; do
  if curl -s "$INFLUX_HOST/ping" >/dev/null 2>&1; then
    echo "InfluxDB reachable"
    break
  fi
  echo "Retrying... ($i)"
  sleep 1
done

if [ "$i" -ge 30 ]; then
  echo "InfluxDB not reachable, exiting"
  exit 1
fi

# Create database (InfluxDB 1.x HTTP API)
curl -s -X POST "$INFLUX_HOST/query?q=CREATE+DATABASE+${DB_NAME}"
echo "Database '${DB_NAME}' created (or already exists)."
