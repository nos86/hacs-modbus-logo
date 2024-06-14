"""Support for Modbus lights."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.modbus.const import CONF_FANS
from homeassistant.components.modbus.fan import ModbusFan
from homeassistant.const import CONF_NAME

from . import get_hub

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

    from .modbus import ModbusHub

PARALLEL_UPDATES = 1


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,  # noqa: ARG001
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Read configuration and create Modbus fans."""
    if discovery_info is None:
        return
    fans = []

    for entry in discovery_info[CONF_FANS]:
        hub: ModbusHub = get_hub(hass, discovery_info[CONF_NAME])
        fans.append(ModbusFan(hass, hub, entry))
    async_add_entities(fans)
