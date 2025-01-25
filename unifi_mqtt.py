import json
import pandas as pd
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
        sanitized_name = name.replace(' ', '_').replace('.', '_').lower()

        # Calculate uptime
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        uptime = f"{days}d {hours}h {minutes}m"

        # Base attributes
        attributes = {
            "type": device_type,
            "status": 'On' if devs.get('state') == 1 else 'Off',
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
            port_poe = {}
            port_power = {}

            # can only get details about ports if the device is enabled
            if devs.get('state') == 1:
                # convert to dataframe, sort and access data from different columns depending upon need
                portTable = pd.DataFrame(devs.get('port_table')).sort_values('port_idx')

                for index, row in portTable.iterrows():
                    port_status[f"port{row['port_idx']}"] = "up" if row['up'] else "down"

                    if 'poe_enable' in portTable.columns:
                        port_poe[f"port{row['port_idx']}"] = "power" if row['poe_enable'] == True else "none"

                    if 'poe_power' in portTable.columns:
                        if (pd.isna(row['poe_power'])):
                            port_power[f"port{row['port_idx']}"] = 0
                        else:
                            port_power[f"port{row['port_idx']}"] = row['poe_power']

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
            vapTable = pd.DataFrame(devs.get('vap_table'))
            # get ssid's that are on channels 1 to 13 = 2.4Ghz
            # get ssid's that are on channels 36 to 165 = 5Ghz

            ghz2_4 = vapTable[vapTable['channel'].between(0,13)].reset_index(inplace = False, drop = True)
            ghz5 = vapTable[vapTable['channel'].between(36,165)].reset_index(inplace = False, drop = True)

            radio_24ghz = {}

            for index, row in ghz2_4.iterrows():
                radio_24ghz[f"ssid{index}"] = {
                    "ssid": row['essid'],
                    "channel": row['channel'],
                    "number_connected": row['num_sta'],
                    "satisfaction": row['satisfaction'],
                    "bytes_rx": row['rx_bytes'],
                    "bytes_tx": row['tx_bytes'],
                    "guest": row['is_guest']
                }

            radio_5ghz = {}

            for index, row in ghz5.iterrows():
                radio_5ghz[f"ssid{index}"] = {
                    "ssid": row['essid'],
                    "channel": row['channel'],
                    "number_connected": row['num_sta'],
                    "satisfaction": row['satisfaction'],
                    "bytes_rx": row['rx_bytes'],
                    "bytes_tx": row['tx_bytes'],
                    "guest": row['is_guest']
                }

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
                "ssids_24ghz": radio_24ghz,
                "ssids_5ghz": radio_5ghz,
            })

        # Add additional attributes for UDM SE
        elif device_type == 'udm':
            # convert to dataframe, sort and access data from different columns depending upon need
            portTable = pd.DataFrame(devs.get('port_table')).sort_values('port_idx')

            port_status = {}
            port_poe = {}
            port_power = {}

            for index, row in portTable.iterrows():
                port_status[row['port_idx']] = "up" if row['up'] else "down"
                port_poe[f"port{row['port_idx']}"] = "power" if row['poe_enable'] else "none"
                port_power[f"port{row['port_idx']}"] = row['poe_power']

            attributes.update({
                "isp_name": devs.get('active_geo_info', {})['WAN'].get('isp_name', 'Unknown'),
                "temperature_0_name": devs.get('temperatures', {})[0].get('name', 0),
                "temperature_0_value": devs.get('temperatures', {})[0].get('value', 0),
                "temperature_1_name": devs.get('temperatures', {})[1].get('name', 0),
                "temperature_1_value": devs.get('temperatures', {})[1].get('value', 0),
                "temperature_2_name": devs.get('temperatures', {})[2].get('name', 0),
                "temperature_2_value": devs.get('temperatures', {})[2].get('value', 0),
                "hostname": devs.get('hostname', 'Unknown'),
                "total_max_power": devs.get('total_max_power', 0),
                "speedtest_rundate": devs.get('speedtest-status', {}).get('rundate', 0),
                "speedtest_latency": devs.get('speedtest-status', {}).get('latency', 0),
                "speedtest_download": devs.get('speedtest-status', {}).get('xput_download', 0),
                "speedtest_upload": devs.get('speedtest-status', {}).get('xput_upload', 0),
                "total_used_power": devs.get('total_used_power', 0),
                "lan_ip": devs.get('lan_ip', 'Unknown'),
                "number_of_connections": devs.get('num_sta', 0), #not ports_used but number of connections, but differs from Unifi UI connection count
                # "ports_used": devs.get('num_sta', 0),
                "ports_user": devs.get('user-num_sta', 0),
                "ports_guest": devs.get('guest-num_sta', 0),
                "active_ports": port_status,
                "poe_ports": port_poe,
                "poe_power": port_power,
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
