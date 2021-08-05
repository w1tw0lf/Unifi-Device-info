# Unifi AP Device info
Provide Unifi device info via api to Home Assistant that will give ap sensors

Thanks to `valvex`, https://community.home-assistant.io/t/monitoring-your-unifi-ap/259703 for giving the base for this.

To get started download, you must have https://github.com/custom-components/sensor.unifigateway install and working

The code above can be used with standalone as with https://github.com/finish06/pyunifi

Made to work with newer UnifiOS

Will give you a card as below:

![ap](https://github.com/w1tw0lf/Unifi-AP-Device-info/blob/main/images/card_ap.png)
![switch](https://github.com/w1tw0lf/Unifi-AP-Device-info/blob/main/images/card_switch.png)

## Scripts

Create a folder `scripts` in your `config` folder and copy the `unifi_ap.py` and/or `unifi_switch.py` into the folder. Edit with details in the section with your details:

```
 - `host`       -- the address of the controller host; IP or name
 - `username`   -- the username to log in with
 - `password`	-- the password to log in with
 - `version`	-- the base version of the controller API [v4|v5|unifiOS|UDMP-unifiOS]
 - `site_id`	-- the site ID to access
 - `port`       -- the port of the controller host
 - `verify_ssl`	-- Verify the controllers SSL certificate, default=True, can also be False or "path/to/custom_cert.pem"
 - `target_mac` -- the mac address of your AP device
```
## Sensor

**For AP:**

Copy the content of `configuration_ap.yaml` to 'configuration.yaml' under sensor.

**For Switch:**

Copy the content of `configuration_switch.yaml` to 'configuration.yaml' under sensor.

## Card

To create the card, you will need https://github.com/benct/lovelace-multiple-entity-row and https://github.com/kalkih/mini-graph-card

**For AP:**

`card_ap.yaml` can be copied to a manual card in the frontend to create card as per image above.

**For Switch:**

`card_switch.yaml` can be copied to a manual card in the frontend to create card as per image above.

## Reboot command

`shell_command.reboot_unifi_ap` can be created via https://github.com/stevejenkins/unifi-linux-utils/blob/master/uap_reboot.sh, change `uap_list` to only the ip of the device.

Then adding to configuration.yaml under shell_command:
```
shell_command:
  reboot_unifi_ap: bash /config/shell/unifi_ap_reboot.sh
```
PS: command works via host, but not in home assistant. Will have to figure this out. Needs `sshpass` in home assistant

## When you have more than one ap/switch

Duplicated as needed per ap and change `unifi_ap` to either ap name or `unifi_ap1` an `unifi_ap2`

Duplicated as needed per ap and change `unifi_switch` to either ap name or `unifi_switch1` an `unifi_switch`

**Remember then to update the sensor and card accordingly**

