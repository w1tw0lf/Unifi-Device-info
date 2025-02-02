"""
Custom component that fetches UniFi device stats and publishes them via MQTT.

This integration queries a UniFi controller for device statistics and publishes
the data via MQTT discovery every 60 seconds.

Due to Home Assistant’s MQTT discovery behavior, if you supply both a sensor “name”
and a device “name” that are identical, Home Assistant will concatenate them.
For example, if both are "UAP NanoHD", the friendly name becomes "UAP NanoHD UAP NanoHD".
There is currently no discovery parameter to disable this behavior.
To have the friendly name display exactly as "UAP NanoHD", you must manually override
the entity’s friendly name in the Home Assistant entity registry after discovery.
"""

import asyncio
import json
import logging
from datetime import timedelta

import pandas as pd
from pyunifi.controller import Controller

from homeassistant.components.mqtt import async_publish
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SITE_ID,
    CONF_PORT,
    CONF_VERIFY_SSL,
    CONF_VERSION,
    UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

# Global variable for the update listener.
UPDATE_LISTENER = None

async def async_setup_entry(hass, entry):
    """Set up the UniFi MQTT integration from a config entry."""
    host = entry.data[CONF_HOST]
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    site_id = entry.data[CONF_SITE_ID]
    port = entry.data[CONF_PORT]
    verify_ssl = entry.data[CONF_VERIFY_SSL]
    version = entry.data[CONF_VERSION]

    def init_controller():
        return Controller(
            host, username, password, port, version, site_id=site_id, ssl_verify=verify_ssl
        )

    try:
        controller = await hass.async_add_executor_job(init_controller)
    except Exception as e:
        _LOGGER.error("Failed to initialize UniFi controller: %s", e)
        return False

    async def update_unifi_data(now):
        """Fetch data from the UniFi controller and publish MQTT discovery and state messages."""
        try:
            unifi_devices = await hass.async_add_executor_job(controller.get_aps)
        except Exception as err:
            _LOGGER.error("Error fetching devices: %s", err)
            return

        for device in unifi_devices:
            if not device.get("adopted"):
                continue

            target_mac = device.get("mac")
            try:
                devs = await hass.async_add_executor_job(controller.get_device_stat, target_mac)
            except Exception as err:
                _LOGGER.error("Error fetching stats for %s: %s", target_mac, err)
                continue

            name = devs.get("name", "Unknown")
            mac = devs.get("mac", "Unknown")
            device_type = devs.get("type", "Unknown")
            uptime_seconds = devs.get("uptime", 0)

            sanitized_name = name.replace(" ", "_").replace(".", "_").lower()

            days = uptime_seconds // 86400
            hours = (uptime_seconds % 86400) // 3600
            minutes = (uptime_seconds % 3600) // 60
            uptime = f"{days}d {hours}h {minutes}m"

            # Build MQTT discovery payload.
            # Note: Both the top-level "name" and the device "name" are set to the device's name.
            # This will cause Home Assistant to concatenate them (e.g., "UAP NanoHD UAP NanoHD").
            # To have the friendly name display as just "UAP NanoHD", you must manually override
            # the entity’s friendly name in the Home Assistant entity registry after discovery.
            discovery_topic = f"homeassistant/sensor/unifi_mqtt/{sanitized_name}/config"
            sensor_payload = {
                "name": name,  # This is the sensor friendly name.
                "object_id": sanitized_name, 
                "state_topic": f"unifi_mqtt/devices/{sanitized_name}/state",
                "unique_id": mac.replace(":", ""),
                "json_attributes_topic": f"unifi_mqtt/devices/{sanitized_name}/attributes",
                "device": {
                    "identifiers": [f"unifi_{mac.replace(':', '')}"],
                    "name": name, 
                    "manufacturer": "UniFi",
                    "model": devs.get("model", "Unknown"),
                    "sw_version": devs.get("version", "Unknown"),
                }
            }
            await async_publish(hass, discovery_topic, json.dumps(sensor_payload), retain=True)

            # Publish the sensor state.
            state_topic = f"unifi_mqtt/devices/{sanitized_name}/state"
            await async_publish(hass, state_topic, uptime, retain=True)

            # Publish sensor attributes.
            attributes_topic = f"unifi_mqtt/devices/{sanitized_name}/attributes"
            attributes = {
                "type": device_type,
                "status": "On" if devs.get("state") == 1 else "Off",
                "mac_address": mac,
                "model": devs.get("model", "Unknown"),
                "cpu": devs.get("system-stats", {}).get("cpu", "N/A"),
                "ram": devs.get("system-stats", {}).get("mem", "N/A"),
                "activity": round(
                    (devs.get("uplink", {}).get("rx_bytes-r", 0) / 125000)
                    + (devs.get("uplink", {}).get("tx_bytes-r", 0) / 125000),
                    1,
                ),
                "bytes_rx": devs.get("rx_bytes", 0),
                "bytes_tx": devs.get("tx_bytes", 0),
                "update": "available" if devs.get("upgradable") else "none",
                "firmware_version": devs.get("version", "Unknown"),
                "ip_address": devs.get("ip", "Unknown"),
            }
            await async_publish(hass, attributes_topic, json.dumps(attributes), retain=True)

    global UPDATE_LISTENER
    UPDATE_LISTENER = async_track_time_interval(
        hass, update_unifi_data, timedelta(seconds=UPDATE_INTERVAL)
    )
    hass.async_create_task(update_unifi_data(None))

    return True

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    global UPDATE_LISTENER
    if UPDATE_LISTENER is not None:
        UPDATE_LISTENER()
        UPDATE_LISTENER = None
    return True
