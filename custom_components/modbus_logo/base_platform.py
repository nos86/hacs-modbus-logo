"""Base implementation for all modbus logo platforms."""

from __future__ import annotations

from typing import TYPE_CHECKING

try:
    import homeassistant.components.modbus.base_platform as base
except ModuleNotFoundError:
    import homeassistant.components.modbus.entity as base
from homeassistant.components.modbus.const import CONF_VERIFY

from .const import CONF_SYNC

if TYPE_CHECKING:
    from datetime import datetime

    from homeassistant.components.modbus.modbus import ModbusHub
    from homeassistant.core import HomeAssistant


class BaseSwitch(base.BaseSwitch):
    """Base class for modbus logo switches."""

    def __init__(self, hass: HomeAssistant, hub: ModbusHub, config: dict) -> None:
        """Initialize the switch."""
        super().__init__(hass, hub, config)
        if self._verify_active:
            self._verify_sync = config[CONF_VERIFY].get(CONF_SYNC, False)

    async def async_update(self, now: datetime | None = None) -> None:
        """Update the entity state."""
        previous_state = self._attr_is_on
        await super().async_update(now)
        if self._attr_is_on != previous_state and self._verify_sync:
            await self._hub.async_pb_call(
                self._slave,
                self._address,
                self.command_on if self._attr_is_on else self._command_off,
                self._write_type,
            )
