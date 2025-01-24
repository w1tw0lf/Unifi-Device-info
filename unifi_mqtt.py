import json
from pyunifi.controller import Controller
from datetime import timedelta

#### Fill in your UniFi controller credentials ####
host = ''
username = ''
password = ''
version = 'UDMP-unifiOS'
site_id = 'default'
port = '443'
verify_ssl = True

################# UniFi Controller ####################
client = Controller(host, username, password, port, version, site_id=site_id, ssl_verify=verify_ssl)
unifi_devices = client.get_aps()

active_devices = []

for device in unifi_devices:
    if device.get('adopted'):
        target_mac = device.get('mac')
        devs = client.get_device_stat(target_mac)

        name = devs.get('name', 'Unknown')
        mac = devs.get('mac', 'Unknown')
        device_type = devs.get('type', 'Unknown')
        uptime_seconds = devs.get('uptime', 0)

        # Sanitize the device name to avoid redundancy
        sanitized_name = name.replace(' ', '_').lower()

        # Calculate uptime
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        uptime = f"{days}d {hours}h {minutes}m"

        # Base attributes
        attributes = {
            "type": device_type,
            "mac_address": mac,
            "model": devs.get('model', 'Unknown'),
            "cpu": devs.get('system-stats', {}).get('cpu', 'N/A'),
            "ram": devs.get('system-stats', {}).get('mem', 'N/A'),
            "activity": round(
                (devs.get('uplink', {}).get('rx_bytes-r', 0) / 125000) +
                (devs.get('uplink', {}).get('tx_bytes-r', 0) / 125000), 1
            ),
            "bytes_rx": devs.get('rx_bytes', 0),
            "bytes_tx": devs.get('tx_bytes', 0),
            "update": "available" if devs.get('upgradable') else "none",
            "firmware_version": devs.get('version', 'Unknown'),
            "ip_address": devs.get('ip', 'Unknown'),
            "device_name": name, # workaround for issue where friendly name duplicates the name
        }

        # Add additional attributes for switches
        if device_type == 'usw':
            port_status = {}
            for index, port in enumerate(devs.get('port_table', []), start=1):
                port_status[f"port{index}"] = "up" if port.get('up') else "down"

            port_poe = {}
            for index, port in enumerate(devs.get('port_table', []), start=1):
                poe_enabled = port.get('poe_enable', False)  # Check if 'poe_enable' is True or False in the port dict
                port_poe[f"port{index}"] = "power" if poe_enabled else "none"

            port_power = {}
            for index, port in enumerate(devs.get('port_table', []), start=1):
                port_power[f"port{index}"] = port.get('poe_power', 0)

            if devs.get('has_temperature'):
                current_temperature = devs.get('general_temperature', 0)
            else:
                current_temperature = 'N/A'

            attributes.update({
                "ports_used": devs.get('num_sta', 0),
                "ports_user": devs.get('user-num_sta', 0),
                "ports_guest": devs.get('guest-num_sta', 0),
                "active_ports": port_status,
                "poe_ports": port_poe,
                "poe_power": port_power,
                "total_used_power": devs.get('total_used_power', 0),
                "current_temperature": current_temperature,
            })


        # Add additional attributes for access points
        elif device_type == 'uap':
            radio_table_stats = devs.get('radio_table_stats', [])
            radio_clients = {}
            radio_scores = {}
            for index, radio in enumerate(radio_table_stats):
                user_num_sta = radio.get('user-num_sta', 0)
                satisfaction = radio.get('satisfaction', 0)
                radio_clients[f"clients_wifi{index}"] = user_num_sta
                radio_scores[f"score_wifi{index}"] = 0 if satisfaction == -1 else satisfaction                      
            attributes.update({
                "clients": devs.get('user-wlan-num_sta', 0),
                "guests": devs.get('guest-wlan-num_sta', 0),
                "score": 0 if devs.get('satisfaction', 0) == -1 else devs.get('satisfaction', 0),
                **radio_clients, 
                **radio_scores,                
            })

        # MQTT Discovery payload
        discovery_topic = f"homeassistant/sensor/{sanitized_name}/config"  # Use sanitized_name here
        sensor_payload = {
            "name": name,  # Device name as it is
            "state_topic": f"unifi/devices/{sanitized_name}/state",  # Use sanitized name in state topic
            "unique_id": mac.replace(':', ''),
            "json_attributes_topic": f"unifi/devices/{sanitized_name}/attributes",  # Attributes topic
            "device": {
                "identifiers": [mac],
                "name": name,
                "manufacturer": "UniFi"
            }
        }

        # Publish MQTT Discovery message
        hass.services.call('mqtt', 'publish', {
            "topic": discovery_topic,
            "payload": json.dumps(sensor_payload),
            "retain": True
        })

        # Publish device state (uptime as state)
        state_topic = f"unifi/devices/{sanitized_name}/state"
        hass.services.call('mqtt', 'publish', {
            "topic": state_topic,
            "payload": uptime,
            "retain": True
        })

        # Publish device attributes
        attributes_topic = f"unifi/devices/{sanitized_name}/attributes"
        hass.services.call('mqtt', 'publish', {
            "topic": attributes_topic,
            "payload": json.dumps(attributes),
            "retain": True
        })

        active_devices.append(name)

# Publish device summary
device_summary_topic = "unifi/devices/summary"
hass.services.call('mqtt', 'publish', {
    "topic": device_summary_topic,
    "payload": json.dumps(active_devices),
    "retain": True
})
