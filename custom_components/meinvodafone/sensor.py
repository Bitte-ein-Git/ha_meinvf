"""Sensor platform."""

from __future__ import annotations
import logging
from datetime import date
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from . import MeinVodafoneCoordinator
from .const import COORDINATOR, DOMAIN
from .MeinVodafoneEntity import MeinVodafoneEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Setup sensor entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    if coordinator.contract:
        entities = [MeinVodafoneSensor(config_entry, coordinator, entity) for entity in coordinator.entities_list if entity.component == "sensor"]
        async_add_entities(entities)

class MeinVodafoneSensor(MeinVodafoneEntity, SensorEntity):
    """Sensor with dynamic units."""
    def __init__(self, config_entry, coordinator, entity) -> None:
        """Init sensor."""
        super().__init__(config_entry, coordinator, entity.attr)
        self._entity = entity
        self._attr_name = entity.name
        self._attr_unique_id = f"{coordinator.contract_id}_{entity.attr}"
        self._attr_has_entity_name = True
        self._attr_icon = entity.icon
        self._attr_device_class = entity.device_class
        self._attr_state_class = entity.state_class
        self._attr_should_poll = False
        self._attr_suggested_display_precision = entity.display_precision
        self._update_state()

    def _update_state(self):
        """Update value and handle date objects."""
        if not self.coordinator.contract: return
        val = getattr(self.coordinator.contract, self.attr, None)
        
        if isinstance(val, date):
            self._attr_native_value = val
            self._attr_native_unit_of_measurement = None
            return

        if self.attr in ["data_remaining", "data_used", "data_total"] and val is not None:
            try:
                mb = float(val)
                if mb >= 1024:
                    self._attr_native_value = round(mb / 1024, 2)
                    self._attr_native_unit_of_measurement = "GiB"
                else:
                    self._attr_native_value = int(mb)
                    self._attr_native_unit_of_measurement = "MiB"
            except (ValueError, TypeError):
                self._attr_native_value = val
                self._attr_native_unit_of_measurement = self._entity.unit
        else:
            self._attr_native_value = val
            self._attr_native_unit_of_measurement = self._entity.unit

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle coordinator update."""
        self._update_state()
        self.async_write_ha_state()