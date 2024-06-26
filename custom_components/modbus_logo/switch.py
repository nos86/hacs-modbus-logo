"""Support for Modbus switches."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_NAME, CONF_SWITCHES

from . import get_hub
from .base_platform import BaseSwitch

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

    from .modbus import ModbusHub

PARALLEL_UPDATES = 1


class ModbusSwitch(BaseSwitch, SwitchEntity):
    """Base class representing a Modbus switch."""

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Set switch on."""
        await self.async_turn(self.command_on, **kwargs)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,  # noqa: ARG001
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Read configuration and create Modbus switches."""
    if discovery_info is None:
        return

    switches = []
    for entry in discovery_info[CONF_SWITCHES]:
        hub: ModbusHub = get_hub(hass, discovery_info[CONF_NAME])
        switches.append(ModbusSwitch(hass, hub, entry))
    async_add_entities(switches)
