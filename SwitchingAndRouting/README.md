# Smart Sensor Gateway Project

## Overview
This project implements a container-based sensor gateway system that collects data from sensors via MQTT, processes it with Node-RED, stores it in a database, and provides visualization through dashboards. The system is managed using Docker Compose and Portainer.

## Architecture
- **MQTT Broker (Mosquitto)**: Handles sensor data publishing
- **Node-RED**: Processes and routes sensor data
- **InfluxDB**: Time-series database for data storage
- **Grafana/Dashboard**: Visualization of sensor data
- **Portainer**: Container management interface

## Installation
1. Ensure Docker and Docker Compose are installed.
2. Clone this repository.
3. Run `docker-compose up -d` to start the services.

## Usage
- Access Node-RED at http://localhost:1880
- Access Portainer at http://localhost:9000 (once added)
- Sensor simulation can be run from the sensor-sim folder.

## Development
- Start with basic MQTT and Node-RED setup.
- Gradually add InfluxDB, monitoring, and automation.

## Team
- [Your name]: Responsible for [components]

## TODO
See session memory for detailed todo list.