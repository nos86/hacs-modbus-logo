"""Support for Modbus Coil and Discrete Input sensors."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.modbus.binary_sensor import (
    ModbusBinarySensor,
    SlaveSensor,
)
from homeassistant.components.modbus.const import (
    CONF_SLAVE_COUNT,
    CONF_VIRTUAL_COUNT,
)
from homeassistant.const import (
    CONF_BINARY_SENSORS,
    CONF_NAME,
)

from . import get_hub

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

PARALLEL_UPDATES = 1


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,  # noqa: ARG001
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Modbus binary sensors."""
    if discovery_info is None:
        return

    sensors: list[ModbusBinarySensor | SlaveSensor] = []
    hub = get_hub(hass, discovery_info[CONF_NAME])
    for entry in discovery_info[CONF_BINARY_SENSORS]:
        slave_count = entry.get(CONF_SLAVE_COUNT, None) or entry.get(
            CONF_VIRTUAL_COUNT, 0
        )
        sensor = ModbusBinarySensor(hass, hub, entry, slave_count)
        if slave_count > 0:
            sensors.extend(await sensor.async_setup_slaves(hass, slave_count, entry))
        sensors.append(sensor)
    async_add_entities(sensors)
