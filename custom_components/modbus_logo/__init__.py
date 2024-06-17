"""
Custom integration to integrate modbus_logo with Home Assistant.

For more details about this integration, please refer to
https://github.com/nos86/hacs-modbus-logo
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast

import homeassistant.components.modbus as mb_component
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.modbus.const import (
    CALL_TYPE_COIL,
    CALL_TYPE_DISCRETE,
    CALL_TYPE_REGISTER_HOLDING,
    CALL_TYPE_REGISTER_INPUT,
    CALL_TYPE_X_COILS,
    CALL_TYPE_X_REGISTER_HOLDINGS,
    CONF_BAUDRATE,
    CONF_BYTESIZE,
    CONF_CLIMATES,
    CONF_FANS,
    CONF_INPUT_TYPE,
    CONF_MSG_WAIT,
    CONF_PARITY,
    CONF_RETRIES,
    CONF_STATE_OFF,
    CONF_STATE_ON,
    CONF_STOPBITS,
    CONF_VERIFY,
    DEFAULT_HUB,
    RTUOVERTCP,
    SERIAL,
    TCP,
    UDP,
)
from homeassistant.components.modbus.modbus import ModbusHub
from homeassistant.components.modbus.validators import struct_validator
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_BINARY_SENSORS,
    CONF_COVERS,
    CONF_DELAY,
    CONF_HOST,
    CONF_LIGHTS,
    CONF_METHOD,
    CONF_NAME,
    CONF_PORT,
    CONF_SENSORS,
    CONF_SWITCHES,
    CONF_TIMEOUT,
    CONF_TYPE,
)

from .const import DOMAIN
from .modbus import async_modbus_setup

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

SWITCH_SCHEMA = mb_component.SWITCH_SCHEMA.extend({})
LIGHT_SCHEMA = mb_component.LIGHT_SCHEMA.extend({})
FAN_SCHEMA = mb_component.FAN_SCHEMA.extend({})

MODBUS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_HUB): cv.string,
        vol.Optional(CONF_TIMEOUT, default=3): cv.socket_timeout,
        vol.Optional(CONF_DELAY, default=0): cv.positive_int,
        vol.Optional(CONF_RETRIES): cv.positive_int,
        vol.Optional(CONF_MSG_WAIT): cv.positive_int,
        vol.Optional(CONF_BINARY_SENSORS): vol.All(
            cv.ensure_list, [mb_component.BINARY_SENSOR_SCHEMA]
        ),
        vol.Optional(CONF_CLIMATES): vol.All(
            cv.ensure_list, [vol.All(mb_component.CLIMATE_SCHEMA, struct_validator)]
        ),
        vol.Optional(CONF_COVERS): vol.All(
            cv.ensure_list, [mb_component.COVERS_SCHEMA]
        ),
        vol.Optional(CONF_LIGHTS): vol.All(cv.ensure_list, [LIGHT_SCHEMA]),
        vol.Optional(CONF_SENSORS): vol.All(
            cv.ensure_list, [vol.All(mb_component.SENSOR_SCHEMA, struct_validator)]
        ),
        vol.Optional(CONF_SWITCHES): vol.All(cv.ensure_list, [SWITCH_SCHEMA]),
        vol.Optional(CONF_FANS): vol.All(cv.ensure_list, [FAN_SCHEMA]),
    }
)

SERIAL_SCHEMA = MODBUS_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): SERIAL,
        vol.Required(CONF_BAUDRATE): cv.positive_int,
        vol.Required(CONF_BYTESIZE): vol.Any(5, 6, 7, 8),
        vol.Required(CONF_METHOD): vol.Any("rtu", "ascii"),
        vol.Required(CONF_PORT): cv.string,
        vol.Required(CONF_PARITY): vol.Any("E", "O", "N"),
        vol.Required(CONF_STOPBITS): vol.Any(1, 2),
    }
)

ETHERNET_SCHEMA = MODBUS_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT): cv.port,
        vol.Required(CONF_TYPE): vol.Any(TCP, UDP, RTUOVERTCP),
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(
            cv.ensure_list,
            [
                vol.Any(SERIAL_SCHEMA, ETHERNET_SCHEMA),
            ],
        ),
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Modbus component."""
    if DOMAIN not in config:
        return True
    return await async_modbus_setup(
        hass,
        config,
    )


def get_hub(hass: HomeAssistant, name: str) -> ModbusHub:
    """Return modbus hub with name."""
    return cast(ModbusHub, hass.data[DOMAIN][name])


async def async_reset_platform(hass: HomeAssistant, _: str) -> None:
    """Release modbus resources."""
    if DOMAIN not in hass.data:
        _LOGGER.error("Modbus cannot reload, because it was never loaded")
        return
    _LOGGER.info("Modbus reloading")
    hubs = hass.data[DOMAIN]
    for name in hubs:
        await hubs[name].async_close()
