"""
Custom integration to integrate modbus_logo with Home Assistant.

For more details about this integration, please refer to
https://github.com/nos86/hacs-modbus-logo
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.modbus import ETHERNET_SCHEMA, SERIAL_SCHEMA
from homeassistant.components.modbus.modbus import ModbusHub

from .const import DOMAIN
from .modbus import async_modbus_setup

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

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
