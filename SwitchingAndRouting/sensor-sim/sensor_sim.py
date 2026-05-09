#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import time
import random
import json
import os

# MQTT settings (use environment variables so the container can connect to the broker service)
BROKER = os.getenv("MQTT_BROKER", "mosquitto")
PORT = int(os.getenv("MQTT_PORT", "1883"))
TOPIC_JOYSTICK = os.getenv("TOPIC_JOYSTICK", "sensor/joystick")
TOPIC_BUTTONS = os.getenv("TOPIC_BUTTONS", "sensor/buttons")

def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected with result code " + str(rc))

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.connect(BROKER, PORT, 60)

client.loop_start()

try:
    while True:
        # Simulate joystick data (x, y coordinates)
        joystick_data = {
            "x": random.uniform(-1.0, 1.0),
            "y": random.uniform(-1.0, 1.0)
        }
        client.publish(TOPIC_JOYSTICK, json.dumps(joystick_data))
        print(f"Published joystick: {joystick_data}")

        # Simulate button data (pressed or not)
        button_data = {
            "button1": random.choice([True, False]),
            "button2": random.choice([True, False])
        }
        client.publish(TOPIC_BUTTONS, json.dumps(button_data))
        print(f"Published buttons: {button_data}")

        time.sleep(1)  # Publish every second

except KeyboardInterrupt:
    print("Stopping simulation")
finally:
    client.loop_stop()
    client.disconnect()