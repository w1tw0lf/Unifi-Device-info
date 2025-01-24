# Unifi AP Device info
Provide Unifi device info via api to Home Assistant that will give ap sensors

Thanks to `valvex`, https://community.home-assistant.io/t/monitoring-your-unifi-ap/259703 for giving the base for this.

To get started download, you must have https://github.com/AlexxIT/PythonScriptsPro added via HACS

Made to work with newer UnifiOS

Will give you a card as below:

![ap](https://github.com/w1tw0lf/Unifi-AP-Device-info/blob/main/images/card_ap.png)
![switch](https://github.com/w1tw0lf/Unifi-AP-Device-info/blob/main/images/card_switch.png)

## Scripts

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
      file: python_scripts/unifi.py
mode: single
```

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/J3J014JZ45)
