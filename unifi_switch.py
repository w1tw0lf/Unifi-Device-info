from pyunifi.controller import Controller
from datetime import timedelta
import json
import re

#### fill in your unifi controller credentials ####

host = 'ip/url'
username = 'username'
password = 'password'
version = 'UDMP-unifiOS'
#### version ####
## the base version of the controller API [v4|v5|unifiOS|UDMP-unifiOS] ##
## this would be for the version of the controller you are running ##
#################
site_id = 'default'
port = '443'
verify_ssl = True
target_mac = '' ## the mac address of your AP device

################# endpoints ####################

client = Controller(host, username, password, port, version,
                          site_id=site_id, ssl_verify=verify_ssl)
stat = client.get_sysinfo()
devs = client.get_device_stat(target_mac)
clients = client.get_clients()
cpu = devs['system-stats']['cpu']
ram = devs['system-stats']['mem']
type = devs['model']
usedports = devs['num_sta']
userports = devs['user-num_sta']
guestports = devs['guest-num_sta']
#temperature = devs['general_temperature']
update = stat[0]['update_available']
activity = round(devs['uplink']['rx_bytes-r']/125000 + devs['uplink']['tx_bytes-r']/125000,1)
seconds = devs['uptime']
days = seconds // 86400
hours = (seconds - (days * 86400)) // 3600
minutes = (seconds - (days * 86400) - (hours * 3600)) // 60
uptime = str(days)+'d '+str(hours)+'h '+str(minutes)+'m'
                                                   
final = json.dumps({"Model":type,"Activity":str(activity)+' Mbps',"CPU":str(cpu),"RAM":str(ram),"Uptime":uptime,"Ports_used":usedports,"Ports_user":userports,"Ports_guest":guestports,"Update":update})

print (final)
                            