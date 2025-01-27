# UniFi Device Info for Home Assistant
UniFi Device Info is a Python-based integration designed to bring real-time monitoring of UniFi network devices into Home Assistant. This tool connects to the UniFi Controller's API to provide comprehensive insights into your network's Access Points (APs) and Switches, providing sensor per device with attributes for various device info.
## Features
- Access Point Monitoring:
  - Live data on connected clients
  - Signal strength for AP per radio
  - Signal strength for AP per SSID
  - Uptime for device
  - Data usage and activity
- Switch Monitoring:
	 - View port statuses, connected devices
  - Data usage and activity
  - POE status if support and power usage per port
 
## Preview

![image](https://github.com/user-attachments/assets/dc63da7e-2d53-4e0c-b28f-100a210f74f7) ![image](https://github.com/user-attachments/assets/21bae16a-2dec-47c2-b774-45905524bfcd)





## Requirements

PythonScriptsPro
	- https://github.com/AlexxIT/PythonScriptsPro added via HACS 

## Installation
Create a folder `python_scripts` in your `config` folder and copy the `unifi_mqtt.py`into the folder. Edit with details in the section with your details:
```
 - `host`       -- the address of the controller host; IP or name
 - `username`   -- the username to log in with
 - `password`	-- the password to log in with
 - `version`	-- the base version of the controller API [v4|v5|unifiOS|UDMP-unifiOS]
 - `site_id`	-- the site ID to access
 - `port`       -- the port of the controller host
 - `verify_ssl`	-- Verify the controllers SSL certificate, default=True, can also be False or "path/to/custom_cert.pem"
```
In the configuration.yaml add

```
python_script:
  requirements:
  - pyunifi
```

## Automation

Create automation:

```
alias: Unifi
description: ""
triggers:
  - trigger: time_pattern
    seconds: "30"
conditions: []
actions:
  - action: python_script.exec
    data:
      file: python_scripts/unifi_mqtt.py
mode: single
```

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/J3J014JZ45)
