# UniFi Device Info Integration

[![HACS Badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://hacs.xyz/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

The **UniFi Device Info Integration** is a custom Home Assistant integration that polls your UniFi controller, by default, every 60 seconds for device statistics and publishes the data via MQTT. The integration creates MQTT discovery messages so that sensors are automatically set up in Home Assistant.

## Features

- **Automatic MQTT Discovery:** Publishes MQTT discovery messages for each device, allowing Home Assistant to automatically configure sensors.
- **Frequent Updates:** Polls your UniFi controller every 60 seconds to update device status, uptime, and detailed attributes.
- **Support for Multiple Device Types:** Handles access points (uap), switches (usw), and UDM devices, publishing relevant attributes for each.
- **UI-Based Configuration:** Configure the integration entirely through Home Assistant’s UI (no manual changes to `configuration.yaml` required).
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
- Select own updating interval (default is 60 seconds)

## Installation

There are two main ways to install the integration:

### 1. Manual Installation

1. Download or clone this repository.
2. Copy the entire `unifi_mqtt` folder into your Home Assistant `custom_components` directory:
   - For Home Assistant OS or Home Assistant Container, this is typically under `/config/custom_components/unifi_mqtt/`.
3. Restart Home Assistant.

### 2. HACS Installation

If you use [HACS](https://hacs.xyz/):
1. Go to **HACS > Integrations**.
2. Click on the three-dot menu in the top right corner and select **Custom repositories**.
3. Enter the URL of this GitHub repository, choose **Integration** as the category, and click **Add**.
4. Install the integration from HACS and restart Home Assistant.

## Configuration

After installation, configure the integration via the Home Assistant UI:

1. Go to **Settings > Devices & Services**.
2. Click on **Add Integration** and search for **"UniFi MQTT"**.
3. Fill in the required details:
   - **Host:** URL or IP address of your UniFi Controller.
   - **Username:** Controller username.
   - **Password:** Controller password.
   - **Site ID:** Typically `default` (unless you use another site).
   - **Port:** Controller port (default is 443).
   - **Verify SSL:** `true` or `false` (depending on your setup).
   - **Version:** Controller version (default is `UDMP-unifiOS`).
   - **Update interval:** How long, in seconds, before refreshing information (default is 60 seconds).
4. Click **Submit** to create the configuration entry.

## How It Works

- **Data Polling:** The integration polls the UniFi controller every 60 seconds for device statistics using the `pyunifi` library.
- **MQTT Publishing:** For each device, it publishes:
  - A **discovery** message to `homeassistant/sensor/unifi/<sanitized_name>/config`
  - A **state** message (showing uptime) to `unifi/devices/<sanitized_name>/state`
  - An **attributes** message with detailed stats to `unifi/devices/<sanitized_name>/attributes`
- A summary of active devices is published to `unifi/devices/summary`.

Ensure that your MQTT integration in Home Assistant is set up and that MQTT discovery is enabled.

## Requirements

- Home Assistant (latest version recommended)
- MQTT Broker configured in Home Assistant
- [pyunifi](https://pypi.org/project/pyunifi/) Python package
- [pandas](https://pandas.pydata.org/) Python package

## Device and sensor naming

Due to Home Assistant’s MQTT discovery behavior, if you supply both a sensor “name” and a device “name” that are identical, Home Assistant will concatenate them.
For example, if both are "UAP NanoHD", the friendly name becomes "UAP NanoHD UAP NanoHD".
There is currently no discovery parameter to disable this behavior.
To have the friendly name display exactly as "UAP NanoHD", you must manually override the entity’s friendly name in the Home Assistant entity registry after discovery.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve this integration.

## License

This project is licensed under the [MIT License](LICENSE).

## Disclaimer

This integration is provided "as is" without any warranty. Use it at your own risk.
