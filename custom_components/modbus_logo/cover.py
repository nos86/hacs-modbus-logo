"""Support for Modbus covers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.modbus.cover import ModbusCover
from homeassistant.const import CONF_COVERS, CONF_NAME

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
    """Read configuration and create Modbus cover."""
    if discovery_info is None:
        return

    covers = []
    for cover in discovery_info[CONF_COVERS]:
        hub: ModbusHub = get_hub(hass, discovery_info[CONF_NAME])
        covers.append(ModbusCover(hass, hub, cover))

    async_add_entities(covers)
