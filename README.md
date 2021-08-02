# Unifi AP Device info
Ubiquiti AP's to Home Assistant that will give ap info

Thanks to `valvex`, https://community.home-assistant.io/t/monitoring-your-unifi-ap/259703 for giving the base for this.

To get started download, you must have https://github.com/custom-components/sensor.unifigateway install and working

The code above can be used with standalone as with https://github.com/finish06/pyunifi

Made to work with newer UnifiOS

The following issues still needs to fixed:

```
Total of all client are shown per on 2.4ghz adn 5ghz
```

Will give you a card as below:

![card](https://github.com/w1tw0lf/Unifi-AP-Device-info/blob/main/images/card.png)

To create the card, you will need https://github.com/benct/lovelace-multiple-entity-row and https://github.com/kalkih/mini-graph-card

Create a folder `scripts` in your `config` folder and copy the `unifi_ap.py` into the folder. Edit with details in the section with your details:

```
host = 'ip/url'
username = 'username'
password = 'password'
```

Add the following to configuration.yaml under sensor:

```
 - platform: command_line
    command: 'python3 /config/scripts/unifi_ap.py'
    command_timeout: 60
    name: unifi_ap
    value_template: '{{ value_json.Clients }}'
    unit_of_measurement: Clients
    scan_interval: 120
    json_attributes:
        - Guests
        - Clients_wifi0
        - Clients_wifi1
        - Score  
        - CPU
        - RAM
        - Uptime
        - Score_wifi0
        - Score_wifi1
        - Activity
        - Update
  - platform: template
    sensors:  
      unifi_ap_guests:
          value_template: >
              {{ states.sensor.unifi_ap.attributes.Guests }}
          friendly_name_template: Unifi AP Guests    
      unifi_ap_activity:
          value_template: >
              {{ states.sensor.unifi_ap.attributes.Activity }}
          unit_of_measurement: 'Mbps'
          friendly_name_template: Unifi AP Activity      
      unifi_ap_ram:
          value_template: >
              {{ states.sensor.unifi_ap.attributes.RAM }}
          unit_of_measurement: '%'
          friendly_name_template: Unifi AP RAM    
      unifi_ap_cpu:
          value_template: >
              {{ states.sensor.unifi_ap.attributes.CPU }}
          unit_of_measurement: '%'
          friendly_name_template: Unifi AP CPU
      unifi_ap_score:
          value_template: >
              {{ states.sensor.unifi_ap.attributes.Score }}
          friendly_name_template: Unifi AP SCORE
      unifi_ap2_score:
          value_template: >
              {% if is_state_attr('sensor.unifi_ap', 'Score_wifi0' , -1) %}
                N/A
              {% else %}
                {{ states.sensor.unifi_ap.attributes.Score_wifi0 }}.
              {% endif %}
          friendly_name_template: Unifi AP 2.4gHz SCORE
      unifi_ap5_score:
          value_template: >
              {% if is_state_attr('sensor.unifi_ap_', 'Score_wifi1' , -1) %}
                N/A
              {% else %}
                {{ states.sensor.unifi_ap.attributes.Score_wifi1 }}.
              {% endif %}
          friendly_name_template: Unifi AP 5gHz SCORE
      unifi_ap_wifi_devices:
          value_template: >
              {{ states.sensor.unifi_ap.attributes.Clients_wifi0 }}
          friendly_name_template: Unifi AP 2.4gHz Clients
      unifi_ap5ghz_wifi_devices:
          value_template: >
              {{ states.sensor.unifi_ap.attributes.Clients_wifi1 }}
          friendly_name_template: Unifi AP 5gHz Clients
      unifi_ap_update:
          value_template: >
              {% if is_state_attr('sensor.unifi_ap', 'Update' , false) %}
                No
              {% else %}
                Available
              {% endif %}
          friendly_name_template: Unifi AP Updates          
```

And create a manual card with the following:

PS: I don't have a `shell_command.reboot_unifi_ap` as I need to figure this out still

```
type: entities
entities:
  - type: 'custom:multiple-entity-row'
    entity: sensor.unifi_ap
    name: Unifi AP
    show_entity_picture: true
    show_state: false
    secondary_info:
      attribute: Uptime
    entities:
      - entity: sensor.unifi_ap_cpu
        name: CPU
      - entity: sensor.unifi_ap_ram
        name: RAM
      - icon: 'mdi:restart'
        tap_action:
          action: call-service
          confirmation: true
          service: shell_command.reboot_unifi_ap
  - type: 'custom:multiple-entity-row'
    entity: sensor.unifi_ap
    icon: 'mdi:devices'
    name: ' '
    show_state: false
    secondary_info:
      entity: sensor.unifi_ap
      name: ' '
    entities:
      - entity: sensor.unifi_ap_wifi_devices
        name: 2.4GhZ
        unit: ' '
      - entity: sensor.unifi_ap5ghz_wifi_devices
        name: 5GhZ
        unit: ' '
      - entity: sensor.unifi_ap_guests
        name: Guests
        unit: ' '
  - type: 'custom:multiple-entity-row'
    entity: sensor.unifi_ap_score
    name: ' '
    icon: 'mdi:percent-outline'
    show_state: false
    secondary_info:
      entity: sensor.unifi_ap_score
      name: ' '
      unit: '% satisfaction'
    entities:
      - entity: sensor.unifi_ap
        attribute: 2gHz
        name: 2gHz
        unit: '%'
        tap_action:
          action: none
      - entity: sensor.unifi_ap
        attribute: 5gHz
        name: 5gHz
        unit: '%'
        tap_action:
          action: none
  - type: 'custom:mini-graph-card'
    entities:
      - entity: sensor.unifi_ap_score
    group: true
    font_size: 85
    hours_to_show: 24
    style: |
      ha-card {
        border-radius: 0px;
        box-shadow: none;
        } 
    show:
      icon: false
      graph: false
      name: false
      state: false
      extrema: true
      average: true
  - type: 'custom:multiple-entity-row'
    entity: sensor.unifi_ap_activity
    name: Activity
    show_state: false
    icon: 'mdi:arrow-up-down'
    secondary_info:
      entity: sensor.unifi_ap_activity
      name: ' '
      unit: ' '
    entities:
      - entity: sensor.unifi_ap_update
        name: New Update
  - type: 'custom:mini-graph-card'
    entities:
      - entity: sensor.unifi_ap_activity
    group: true
    hours_to_show: 4
    line_width: 3
    points_per_hour: 15
    show:
      icon: false
      name: false
      state: false
      labels: true
```
