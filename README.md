[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

# Home Assistant Custom Integration: modbus_logo

[modbus](http://www.modbus.org/) is a communication protocol to control PLCs (Programmable Logic Controller) and RTUs (Remote Terminal Unit).

The integration adheres to the [protocol specification](https://www.modbus.org/docs/Modbus_Application_Protocol_V1_1b3.pdf) using [pymodbus](https://github.com/pymodbus-dev/pymodbus) for the protocol implementation.

The modbus_logo *custom integration* supports all devices adhering to the modbus standard. The communication to the device/devices can be serial (rs-485), TCP, or UDP connections. The modbus integration allows multiple communication channels e.g. a serial port connection combined with one or more TCP connections.

This integration is built on top of official components in home-assistant and extend some functionality.
Documentation of this integration is the same of the official [documentation](https://www.home-assistant.io/integrations/modbus/).

Continuing in the reading of this file you'll find the documentation for the added specific feature.


## Supported entity

Currently (HA core v2024.6.0) all entities already supported by official component are supported:
- binary_sensor
- climate
- cover
- fan
- light
- sensor
- switch

## Prerequisites

* [Home Assistant (hass)](https://www.home-assistant.io/) >= 2022.0.
* [pymodbus](https://github.com/pymodbus-dev/pymodbus) == 3.6.8 will load automatically.

## Installation

> **Note**
> This integration requires [HACS](https://hacs.xyz/docs/setup/download/) to be installed

1. Open HACS
2. Open the options in the top right and select _Custom repositories_
3. Enter this repository's URL (`https://github.com/AndyGybels/modbus-pulse`) under the Category _Integration_.
4. Press _Add_
5. _+ EXPLORE & DOWNLOAD REPOSITORIES_
6. Find _Modbus Pulse_ in this list
7. _DOWNLOAD THIS REPOSITORY WITH HACS_
8. _DOWNLOAD_
9. Restart Home Assistant (_Settings_ > _System_ >  _RESTART_)

## Configuration

modbus_logo is configured in the `configuration.yaml` file under the *modbus_logo* domain.
Configuration is the same as the integrated modbus integration so see the modbus integration documentation for more information:
https://www.home-assistant.io/integrations/modbus/

If you have already the modbus component configured, to switch to modbus_plc is enough to rename the key in your configuration file from *modbus* to *modbus_plc*


## Opening an issue

Please open issue, only in case of issues related to extension in this repository

