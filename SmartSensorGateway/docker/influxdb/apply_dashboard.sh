#!/bin/sh
# Waits for InfluxDB, substitutes env-var placeholders in the dashboard
# template (e.g. ${INFLUXDB_BUCKET}), then applies it with influx apply.
set -e

until influx ping --host "http://influxdb:${INFLUXDB_PORT}" > /dev/null 2>&1; do
  echo "Waiting for InfluxDB..."
  sleep 2
done

echo "Substituting variables in dashboard template..."
sed "s|\${INFLUXDB_BUCKET}|${INFLUXDB_BUCKET}|g" /data/sensor_dashboard.yaml > /tmp/sensor_dashboard.yaml

echo "Importing dashboard..."
if influx apply --force yes \
  --host "http://influxdb:${INFLUXDB_PORT}" \
  --token "${INFLUXDB_TOKEN}" \
  --org "${INFLUXDB_ORG}" \
  -f /tmp/sensor_dashboard.yaml; then
  echo "Dashboard imported successfully."
else
  echo "Import failed."
fi