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
- Access Portainer at http://localhost:9000 

## Development


## Team
Jamie Jones
## Deployment
I have also setup a proxmox server at home on which I have setup a VM with ubuntu-24.04.4-live-server-amd64.iso on this VM I installed docker and docker-compose.
As you can see in the screenshots below, we are able to acces all our Containers form my Local Network.
![Proxmox](image.png)
![InfluxDB](image-1.png)
![NodeRed](image-2.png)
![Portainer](image-3.png)