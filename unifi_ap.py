from pyunifi.controller import Controller
from datetime import timedelta
import json
import re

#### fill in your unifi controller credentials ####

host = 'ip/url'
username = 'username'
password = 'password'
version = 'UDMP-unifiOS'
site_id = 'default'
port = '443'
verify_ssl = True
target_mac = '' ## the mac address of your AP device
################# Wifi Radio's ####################
# for wifi 6 use:
# ra0 for 2.4ghz clients
# rai0 for 5ghz clients
# for wifi use:
# wifi0 for 2.4ghz clients
# wifi1 for 5ghz clients

clients24 = 'wifi0'
clients5 = 'wifi1'

################# endpoints ####################

client = Controller(host, username, password, port, version,
                          site_id=site_id, ssl_verify=verify_ssl)
stat = client.get_sysinfo()
devs = client.get_device_stat(target_mac)
clients = client.get_clients()
#guests = client.authorize_guest()

###########################################

numclients = devs['user-wlan-num_sta']
numguests = devs['guest-wlan-num_sta']
score = devs['satisfaction']
update = stat[0]['update_available']
cpu = devs['system-stats']['cpu']
ram = devs['system-stats']['mem']

activity = round(devs['uplink']['rx_bytes-r']/125000 + devs['uplink']['tx_bytes-r']/125000,1)
seconds = devs['uptime']
days = seconds // 86400
hours = (seconds - (days * 86400)) // 3600
minutes = (seconds - (days * 86400) - (hours * 3600)) // 60
uptime = str(days)+'d '+str(hours)+'h '+str(minutes)+'m'

### Wifi Clients and score ###
# Remember to adjust according to the number of your ssids #

wifi0clients = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(clients24), str(clients)))
wifi1clients = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(clients5), str(clients)))
wifi0score = devs['radio_table_stats'][0]['satisfaction']
wifi1score = devs['radio_table_stats'][1]['satisfaction']

### Wifi Clients Names###
# You can further specify the clients name in total or per ssid with the following #
# allclients = ",".join([str([x][0]['name']) for x in clients]) #
# wifi1clientnames = ','.join([clients[i]['name']for i in [i for i,x in enumerate(clients) if 'wifi1' in str(x)]]) #
# wifi0clientnames = ','.join([clients[i]['name']for i in [i for i,x in enumerate(clients) if 'wifi0' in str(x)]]) #
# It's been reported that this doesn't work for some users, so give it a try first. #
# Remember to add the keys allclients, wifi1clientnames, wifi0clientnames in your final json and on your sensor's config in HA. #


                                                   
final = json.dumps({"Clients":numclients,"Guests":numguests,"Clients_wifi0":wifi0clients ,"Clients_wifi1":wifi1clients ,"Score":score,"CPU":str(cpu),"RAM":str(ram),"Uptime":uptime,"Score_wifi0":wifi0score ,"Score_wifi1":wifi1score ,\
                "Activity":str(activity)+' Mbps',"Update":update})

print (final)
                            
