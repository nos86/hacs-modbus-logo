"""Support for Modbus."""

from __future__ import annotations

import logging
from collections import namedtuple
from typing import TYPE_CHECKING

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.modbus.const import (
    ATTR_ADDRESS,
    ATTR_HUB,
    ATTR_SLAVE,
    ATTR_UNIT,
    ATTR_VALUE,
    CALL_TYPE_WRITE_COIL,
    CALL_TYPE_WRITE_COILS,
    CALL_TYPE_WRITE_REGISTER,
    CALL_TYPE_WRITE_REGISTERS,
    DEFAULT_HUB,
    PLATFORMS,
    SERVICE_RESTART,
    SERVICE_STOP,
    SERVICE_WRITE_COIL,
    SERVICE_WRITE_REGISTER,
    SIGNAL_START_ENTITY,
    SIGNAL_STOP_ENTITY,
)
from homeassistant.components.modbus.modbus import ModbusHub
from homeassistant.components.modbus.validators import check_config
from homeassistant.const import (
    ATTR_STATE,
    CONF_NAME,
    EVENT_HOMEASSISTANT_STOP,
)
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.issue_registry import IssueSeverity, async_create_issue
from homeassistant.helpers.reload import async_setup_reload_service

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import Event, HomeAssistant, ServiceCall
    from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)


ConfEntry = namedtuple("ConfEntry", "call_type attr func_name")  # noqa: PYI024
RunEntry = namedtuple("RunEntry", "attr func")  # noqa: PYI024
PB_CALL = []


async def async_modbus_setup(
    hass: HomeAssistant,
    config: ConfigType,
) -> bool:
    """Set up Modbus component."""
    await async_setup_reload_service(hass, DOMAIN, [DOMAIN])

    if config[DOMAIN]:
        config[DOMAIN] = check_config(hass, config[DOMAIN])
        if not config[DOMAIN]:
            return False
    if DOMAIN in hass.data and config[DOMAIN] == []:
        hubs = hass.data[DOMAIN]
        for name in hubs:
            if not await hubs[name].async_setup():
                return False
        hub_collect = hass.data[DOMAIN]
    else:
        hass.data[DOMAIN] = hub_collect = {}

    for conf_hub in config[DOMAIN]:
        my_hub = ModbusHub(hass, conf_hub)
        hub_collect[conf_hub[CONF_NAME]] = my_hub

        # modbus needs to be activated before components are loaded
        # to avoid a racing problem
        if not await my_hub.async_setup():
            return False

        # load platforms
        for component, conf_key in PLATFORMS:
            if conf_key in conf_hub:
                hass.async_create_task(
                    async_load_platform(hass, component, DOMAIN, conf_hub, config)
                )

    async def async_stop_modbus(_: Event) -> None:
        """Stop Modbus service."""
        async_dispatcher_send(hass, SIGNAL_STOP_ENTITY)
        for client in hub_collect.values():
            await client.async_close()

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, async_stop_modbus)

    async def async_write_register(service: ServiceCall) -> None:
        """Write Modbus registers."""
        slave = 0
        if ATTR_UNIT in service.data:
            slave = int(float(service.data[ATTR_UNIT]))

        if ATTR_SLAVE in service.data:
            slave = int(float(service.data[ATTR_SLAVE]))
        address = int(float(service.data[ATTR_ADDRESS]))
        value = service.data[ATTR_VALUE]
        hub = hub_collect[service.data.get(ATTR_HUB, DEFAULT_HUB)]
        if isinstance(value, list):
            await hub.async_pb_call(
                slave,
                address,
                [int(float(i)) for i in value],
                CALL_TYPE_WRITE_REGISTERS,
            )
        else:
            await hub.async_pb_call(
                slave, address, int(float(value)), CALL_TYPE_WRITE_REGISTER
            )

    async def async_write_coil(service: ServiceCall) -> None:
        """Write Modbus coil."""
        slave = 0
        if ATTR_UNIT in service.data:
            slave = int(float(service.data[ATTR_UNIT]))
        if ATTR_SLAVE in service.data:
            slave = int(float(service.data[ATTR_SLAVE]))
        address = service.data[ATTR_ADDRESS]
        state = service.data[ATTR_STATE]
        hub = hub_collect[service.data.get(ATTR_HUB, DEFAULT_HUB)]
        if isinstance(state, list):
            await hub.async_pb_call(slave, address, state, CALL_TYPE_WRITE_COILS)
        else:
            await hub.async_pb_call(slave, address, state, CALL_TYPE_WRITE_COIL)

    for x_write in (
        (SERVICE_WRITE_REGISTER, async_write_register, ATTR_VALUE, cv.positive_int),
        (SERVICE_WRITE_COIL, async_write_coil, ATTR_STATE, cv.boolean),
    ):
        hass.services.async_register(
            DOMAIN,
            x_write[0],
            x_write[1],
            schema=vol.Schema(
                {
                    vol.Optional(ATTR_HUB, default=DEFAULT_HUB): cv.string,  # type: ignore  # noqa: PGH003
                    vol.Exclusive(ATTR_SLAVE, "unit"): cv.positive_int,
                    vol.Exclusive(ATTR_UNIT, "unit"): cv.positive_int,
                    vol.Required(ATTR_ADDRESS): cv.positive_int,
                    vol.Required(x_write[2]): vol.Any(
                        cv.positive_int, vol.All(cv.ensure_list, [x_write[3]])
                    ),
                }
            ),
        )

    async def async_stop_hub(service: ServiceCall) -> None:
        """Stop Modbus hub."""
        async_dispatcher_send(hass, SIGNAL_STOP_ENTITY)
        hub = hub_collect[service.data[ATTR_HUB]]
        await hub.async_close()

    async def async_restart_hub(service: ServiceCall) -> None:
        """Restart Modbus hub."""
        async_create_issue(
            hass,
            DOMAIN,
            "deprecated_restart",
            breaks_in_ha_version="2024.11.0",
            is_fixable=False,
            severity=IssueSeverity.WARNING,
            translation_key="deprecated_restart",
        )
        _LOGGER.warning(
            "`modbus.restart` is deprecated and will be removed in version 2024.11"
        )
        async_dispatcher_send(hass, SIGNAL_START_ENTITY)
        hub = hub_collect[service.data[ATTR_HUB]]
        await hub.async_restart()

    for x_service in (
        (SERVICE_STOP, async_stop_hub),
        (SERVICE_RESTART, async_restart_hub),
    ):
        hass.services.async_register(
            DOMAIN,
            x_service[0],
            x_service[1],
            schema=vol.Schema({vol.Required(ATTR_HUB): cv.string}),
        )
    return True
