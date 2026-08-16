#!/usr/bin/env python3
import json
import os
import random
import time

import paho.mqtt.client as mqtt

BROKER = (os.getenv("MQTT_BROKER") or "mosquitto").strip()
PORT = int((os.getenv("MQTT_PORT") or "1883").strip())
TOPIC_JOYSTICK = (os.getenv("TOPIC_JOYSTICK") or "sensor/joystick").strip()
TOPIC_BUTTONS = (os.getenv("TOPIC_BUTTONS") or "sensor/buttons").strip()

print(f"Connecting to MQTT broker {BROKER}:{PORT}")


def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Connected with result code {rc}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.connect(BROKER, PORT, 60)
client.loop_start()

try:
    while True:
        joystick = {
            "x": round(random.uniform(-1.0, 1.0), 2),
            "y": round(random.uniform(-1.0, 1.0), 2),
        }
        buttons = {
            "button1": random.choice([True, False]),
            "button2": random.choice([True, False]),
        }

        client.publish(TOPIC_JOYSTICK, json.dumps(joystick))
        client.publish(TOPIC_BUTTONS, json.dumps(buttons))
        print(f"Published joystick={joystick} buttons={buttons}")
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping simulation")
finally:
    client.loop_stop()
    client.disconnect()
