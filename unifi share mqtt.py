from typing import final
from pyunifi.controller import Controller
from datetime import timedelta
import re
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

################# MQTT Setup ####################
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(mqtt_username, mqtt_password)
mqtt_client.connect(mqtt_broker, mqtt_port, 60)

################# UniFi Controller ####################
client = Controller(host, username, password, port, version,
                          site_id=site_id, ssl_verify=verify_ssl)
unifi_devices = client.get_aps()

active_device = []
for du in range(len(unifi_devices)):
    adopted = unifi_devices[du]['adopted']
    if adopted:
        target_mac = unifi_devices[du]['mac']
        stat = client.get_sysinfo()
        devs = client.get_device_stat(target_mac)
        clients = client.get_clients()
        cpu = devs['system-stats']['cpu']
        ram = devs['system-stats']['mem']
        model = devs['model']
        type = devs['type']
        name = devs['name']
        update = "available" if devs['upgradable'] else "none"
        activity = round(devs['uplink']['rx_bytes-r'] / 125000 + devs['uplink']['tx_bytes-r'] / 125000, 1)
        seconds = devs['uptime']
        days = seconds // 86400
        hours = (seconds - (days * 86400)) // 3600
        minutes = (seconds - (days * 86400) - (hours * 3600)) // 60
        uptime = f"{days}d {hours}h {minutes}m"
        
        device_info = {
            "Friendly name": name,
            "Model": model,
            "Type": type,
            "Activity": f"{activity} Mbps",
            "CPU": str(cpu),
            "RAM": str(ram),
            "Uptime": uptime,
            "Update": update,
        }

        # Handle specific device types
        if type == 'usw':
            usedports = devs['num_sta']
            userports = devs['user-num_sta']
            guestports = devs['guest-num_sta']
            ports = [
                "up" if port['up'] else "down"
                for port in devs['port_table']
            ]
            device_info.update({
                "Ports_used": usedports,
                "Ports_user": userports,
                "Ports_guest": guestports,
                "Active_ports": ports,
            })

        elif type == 'uap':
            numclients = devs['user-wlan-num_sta']
            numguests = devs['guest-wlan-num_sta']
            wifi0clients = devs['radio_table_stats'][0]['user-num_sta']
            wifi1clients = devs['radio_table_stats'][1]['user-num_sta']
            wifi0score = devs['radio_table_stats'][0]['satisfaction']
            wifi1score = devs['radio_table_stats'][1]['satisfaction']
            device_info.update({
                "Clients": numclients,
                "Guests": numguests,
                "Clients_wifi0": wifi0clients,
                "Clients_wifi1": wifi1clients,
                "Score_wifi0": wifi0score,
                "Score_wifi1": wifi1score,
            })
        
        # Publish to MQTT
        topic = f"{mqtt_topic_prefix}{name.replace(' ', '_')}"
        mqtt_client.publish(topic, payload=str(device_info))
        active_device.append(name)

# Publish device summary
device_summary_topic = f"{mqtt_topic_prefix}summary"
mqtt_client.publish(device_summary_topic, payload=str(active_device))

# Disconnect MQTT client
mqtt_client.disconnect()
