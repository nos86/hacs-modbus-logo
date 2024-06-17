"""Base implementation for all modbus logo platforms."""

from __future__ import annotations

from typing import TYPE_CHECKING

import homeassistant.components.modbus.base_platform as base

if TYPE_CHECKING:
    from datetime import datetime

    from homeassistant.components.modbus.modbus import ModbusHub
    from homeassistant.core import HomeAssistant


class BaseSwitch(base.BaseSwitch):
    """Base class for modbus logo switches."""

    def __init__(self, hass: HomeAssistant, hub: ModbusHub, config: dict) -> None:
        """Initialize the switch."""
        super().__init__(hass, hub, config)

    async def async_update(self, now: datetime | None = None) -> None:
        """Update the entity state."""
        await super().async_update(now)
