FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY sensor_sim.py ./

# Default broker to the mosquitto service name on the compose network
ENV MQTT_BROKER=mosquitto
ENV MQTT_PORT=1883

CMD ["python", "sensor_sim.py"]
