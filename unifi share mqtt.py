import json
from pyunifi.controller import Controller
from datetime import timedelta
import paho.mqtt.client as mqtt

#### Fill in your UniFi controller credentials ####
host = ''
username = ''
password = ''
version = 'UDMP-unifiOS'
site_id = 'default'
port = '443'
verify_ssl = True

#### Fill in your MQTT broker details ####
mqtt_broker = "mqtt.example.com"
mqtt_port = 1883
mqtt_username = "mqtt_user"
mqtt_password = "mqtt_password"
mqtt_topic_prefix = "unifi/devices/"
mqtt_discovery_prefix = "homeassistant"

################# MQTT Setup ####################
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(mqtt_username, mqtt_password)
mqtt_client.connect(mqtt_broker, mqtt_port, 60)

################# UniFi Controller ####################
client = Controller(host, username, password, port, version, site_id=site_id, ssl_verify=verify_ssl)
unifi_devices = client.get_aps()

active_devices = []

for device in unifi_devices:
    if device.get('adopted'):
        target_mac = device.get('mac')
        devs = client.get_device_stat(target_mac)

        name = devs.get('name', 'Unknown')
        model = devs.get('model', 'Unknown')
        mac = devs.get('mac', 'Unknown')
        device_type = devs.get('type', 'Unknown')
        uptime_seconds = devs.get('uptime', 0)

        # Calculate uptime
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        uptime = f"{days}d {hours}h {minutes}m"

        # Base attributes
        attributes = {
            "type": device_type,
            "uptime": uptime,
            "cpu": devs.get('system-stats', {}).get('cpu', 'N/A'),
            "ram": devs.get('system-stats', {}).get('mem', 'N/A'),
            "activity": round(
                (devs.get('uplink', {}).get('rx_bytes-r', 0) / 125000) +
                (devs.get('uplink', {}).get('tx_bytes-r', 0) / 125000), 1
            ),
            "update": "available" if devs.get('upgradable') else "none",
        }

        # Add additional attributes for switches
        if device_type == 'usw':
            port_status = {}
            for index, port in enumerate(devs.get('port_table', []), start=1):
                port_status[f"port{index}"] = "up" if port.get('up') else "down"

            attributes.update({
                "ports_used": devs.get('num_sta', 0),
                "ports_user": devs.get('user-num_sta', 0),
                "ports_guest": devs.get('guest-num_sta', 0),
                "active_ports": port_status,
            })

        # Add additional attributes for access points
        elif device_type == 'uap':
            attributes.update({
                "clients": devs.get('user-wlan-num_sta', 0),
                "guests": devs.get('guest-wlan-num_sta', 0),
                "clients_wifi0": devs.get('radio_table_stats', [{}])[0].get('user-num_sta', 0),
                "clients_wifi1": devs.get('radio_table_stats', [{}])[1].get('user-num_sta', 0),
                "score_wifi0": devs.get('radio_table_stats', [{}])[0].get('satisfaction', 0),
                "score_wifi1": devs.get('radio_table_stats', [{}])[1].get('satisfaction', 0),
            })

        # MQTT Discovery payload
        discovery_topic = f"{mqtt_discovery_prefix}/sensor/{mac.replace(':', '')}/config"
        sensor_payload = {
            "name": name,
            "state_topic": f"{mqtt_topic_prefix}{name.replace(' ', '_')}/state",
            "unique_id": mac.replace(':', ''),
            "json_attributes_topic": f"{mqtt_topic_prefix}{name.replace(' ', '_')}/attributes",
            "device": {
                "identifiers": [mac],
                "name": name,
                "model": model,
                "manufacturer": "UniFi"
            }
        }

        # Publish MQTT Discovery message
        mqtt_client.publish(discovery_topic, payload=json.dumps(sensor_payload), retain=True)

        # Publish device state (model as state)
        state_topic = f"{mqtt_topic_prefix}{name.replace(' ', '_')}/state"
        mqtt_client.publish(state_topic, payload=model, retain=True)

        # Publish device attributes
        attributes_topic = f"{mqtt_topic_prefix}{name.replace(' ', '_')}/attributes"
        mqtt_client.publish(attributes_topic, payload=json.dumps(attributes), retain=True)

        active_devices.append(name)

# Publish device summary
device_summary_topic = f"{mqtt_topic_prefix}summary"
mqtt_client.publish(device_summary_topic, payload=json.dumps(active_devices), retain=True)

# Disconnect MQTT client
mqtt_client.disconnect()

