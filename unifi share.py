from typing import final
from pyunifi.controller import Controller
from datetime import timedelta
import json
import re

#### fill in your unifi controller credentials ####

host = ''
username = ''
password = ''
version = 'UDMP-unifiOS'
site_id = 'default'
port = '443'
verify_ssl = True

################# endpoints ####################

client = Controller(host, username, password, port, version,
                          site_id=site_id, ssl_verify=verify_ssl)
unifi_devices = client.get_aps()

device = []
for du in range(len(unifi_devices)):
    adopted = unifi_devices[du]['adopted']
    if adopted == True:
        device.append({unifi_devices[du]['mac']})

active_device = []
for d in range(len(device)):
    target_mac = unifi_devices[d]['mac']
    stat = client.get_sysinfo()
    devs = client.get_device_stat(target_mac)
    clients = client.get_clients()
    cpu = devs['system-stats']['cpu']
    ram = devs['system-stats']['mem']
    model = devs['model']
    type = devs['type']
    name = devs['name']
    if devs['upgradable'] == True:
        update = "available"
    else:
        update = 'none'
    activity = round(devs['uplink']['rx_bytes-r']/125000 + devs['uplink']['tx_bytes-r']/125000,1)
    seconds = devs['uptime']
    days = seconds // 86400
    hours = (seconds - (days * 86400)) // 3600
    minutes = (seconds - (days * 86400) - (hours * 3600)) // 60
    uptime = str(days)+'d '+str(hours)+'h '+str(minutes)+'m'
    device_info = []
    if type == 'usw':
        usedports = devs['num_sta']
        userports = devs['user-num_sta']
        guestports = devs['guest-num_sta']
        ports = []
        for x in range(len(devs['port_table'])):
            port = devs['port_table'][x]['up']
            if port == True:
                ports.append("up")
            else:
                ports.append("down")
        device_name = name.replace(' ', '_')
        active_device.append(device_name)
        active_ports= []
        for ap in range(len(ports)):
            active_ports.append({"Port" + str(ap+1):ports[ap]})                      
        if "P" in model:
            table = (devs['port_table'])
            length = len(table)
            count = 0
            def count_port_enabled(obj):
                global count
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key == "poe_enable":
                            count += 1
                        count_port_enabled(value)
                elif isinstance(obj, list):
                    for item in obj:
                        count_port_enabled(item)
            for entry in table:
                count_port_enabled(entry)
            poe = length - count
            if "USF" in model:
                ports_poe = []
                for x in range(len(table) - poe):
                    port = devs['port_table'][x + 1]['poe_enable']
                    if port  == True:
                        ports_poe.append("power")
                    else:
                        ports_poe.append("none")
                device_name = name.replace(' ', '_')
                active_device.append(device_name)
                poe_ports= []
                for ap in range(len(ports_poe)):
                    poe_ports.append({"Port" + str(ap+2):ports_poe[ap]})             
            else:
                ports_poe = []
                for x in range(len(table) - poe):
                    port = devs['port_table'][x]['poe_enable']
                    if port == True:
                        ports_poe.append("power")
                    else:
                        ports_poe.append("none")
                device_name = name.replace(' ', '_')
                active_device.append(device_name)
                poe_ports= []
                for ap in range(len(ports_poe)):
                    poe_ports.append({"Port" + str(ap+1):ports_poe[ap]})
        else:
            poe_ports = "none"                                                             
        results = json.dumps({"Friendly name":name,"Model":model,"Type":type,"Activity":str(activity)+' Mbps',"CPU":str(cpu),"RAM":str(ram),"Uptime":uptime,"Ports_used":usedports,"Ports_user":userports,"Ports_guest":guestports,"Update":update,"activeports":active_ports,"poeports":poe_ports})
        output_filename = 'device_' + device_name + '.json'
        with open(output_filename, 'w') as output:
            output.write(results)    

    elif type == 'uap':
        numclients = devs['user-wlan-num_sta']
        numguests = devs['guest-wlan-num_sta']
        score = devs['satisfaction']
        wifi0clients = devs['radio_table_stats'][0]['user-num_sta']
        wifi1clients = devs['radio_table_stats'][1]['user-num_sta']
        wifi0score = devs['radio_table_stats'][0]['satisfaction']
        wifi1score = devs['radio_table_stats'][1]['satisfaction']
        results = json.dumps({"Friendly name":name,"Model":model,"Type":type,"Clients":numclients,"Guests":numguests,"Clients_wifi0":wifi0clients ,"Clients_wifi1":wifi1clients ,"Score":score,"CPU":str(cpu),"RAM":str(ram),"Uptime":uptime,"Score_wifi0":wifi0score ,"Score_wifi1":wifi1score ,"Activity":str(activity)+' Mbps',"Update":update})
        device_name = name.replace(' ', '_')
        active_device.append(device_name)
        output_filename = 'device_' + device_name + '.json'
        with open(output_filename, 'w') as output:
            output.write(results)

index = 0 
device_results = []      
while index < len(active_device):
        device_results.append({"Device" + str(index+1):active_device[index]})
        index = index + 1
deviceresults = json.dumps(device_results)
output_filename = 'devices.json'
with open(output_filename, 'w') as output:
    output.write(deviceresults)


