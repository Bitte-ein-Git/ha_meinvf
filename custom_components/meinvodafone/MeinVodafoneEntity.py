"""MeinVodafone Entity Base."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

class MeinVodafoneEntity(CoordinatorEntity):
    """Base class for device logic."""

    def __init__(self, config_entry, coordinator, attr) -> None:
        """Init base."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.attr = attr

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info with transformed MSISDN (49 to 0)."""
        msisdn = self.coordinator.contract_id
        display_msisdn = msisdn
        if msisdn.startswith("49"):
            display_msisdn = "0" + msisdn[2:]
            
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.contract_id)},
            name=display_msisdn,
            manufacturer="Vodafone",
            model="Mobile Contract",
        )