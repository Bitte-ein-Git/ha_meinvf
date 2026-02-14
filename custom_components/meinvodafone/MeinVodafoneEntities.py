"""MeinVodafone Entities."""

import logging
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.components.sensor.const import UnitOfTime
from homeassistant.const import CURRENCY_EURO
from .MeinVodafoneContract import MeinVodafoneContract

_LOGGER = logging.getLogger(__name__)

class BaseEntity:
    """Entity base."""
    def __init__(self, component, attr, name, icon=None, device_class=None, state_class=None, precision=None):
        self.attr = attr
        self.component = component
        self.name = name
        self.icon = icon
        self.device_class = device_class
        self.state_class = state_class
        self.display_precision = precision
        self.contract = None

    def setup(self, contract) -> bool:
        """Validate support."""
        self.contract = contract
        return getattr(self.contract, f"is_{self.attr}_supported", False)

class Sensor(BaseEntity):
    """Sensor spec."""
    def __init__(self, attr, name, icon, unit, device_class=None, state_class=None, precision=None):
        super().__init__("sensor", attr, name, icon, device_class, state_class, precision)
        self.unit = unit

def create_entities() -> list[Sensor]:
    """Return all sensors."""
    return [
        Sensor("plan_name", "Plan name", "mdi:cellphone-information", None),
        Sensor("plan_price", "Plan price", "mdi:cash-multiple", None),
        Sensor("data_available_until", "Data available until", "mdi:calendar-clock", None, device_class=SensorDeviceClass.DATE),
        Sensor("minutes_remaining", "Minutes remaining", "mdi:clock-plus", UnitOfTime.MINUTES, state_class=SensorStateClass.MEASUREMENT),
        Sensor("minutes_used", "Minutes used", "mdi:clock-minus", UnitOfTime.MINUTES, state_class=SensorStateClass.MEASUREMENT),
        Sensor("minutes_total", "Minutes total", "mdi:clock-check", UnitOfTime.MINUTES, state_class=SensorStateClass.MEASUREMENT),
        Sensor("sms_remaining", "SMS remaining", "mdi:message-plus", "sms", state_class=SensorStateClass.MEASUREMENT),
        Sensor("sms_used", "SMS used", "mdi:message-minus", "sms", state_class=SensorStateClass.MEASUREMENT),
        Sensor("sms_total", "SMS total", "mdi:message-check", "sms", state_class=SensorStateClass.MEASUREMENT),
        Sensor("data_remaining", "Data remaining", "mdi:web-plus", "MiB", device_class=SensorDeviceClass.DATA_SIZE, state_class=SensorStateClass.MEASUREMENT),
        Sensor("data_used", "Data used", "mdi:web-minus", "MiB", device_class=SensorDeviceClass.DATA_SIZE, state_class=SensorStateClass.MEASUREMENT),
        Sensor("data_total", "Data total", "mdi:web-check", "MiB", device_class=SensorDeviceClass.DATA_SIZE, state_class=SensorStateClass.MEASUREMENT),
        Sensor("billing_current_summary", "Billing current summary", "mdi:credit-card-search", CURRENCY_EURO, state_class=SensorStateClass.MEASUREMENT),
        Sensor("billing_last_summary", "Billing last summary", "mdi:credit-card-clock", CURRENCY_EURO, state_class=SensorStateClass.MEASUREMENT),
        Sensor("billing_cycle_days", "Next billing cycle in", "mdi:credit-card-sync", UnitOfTime.DAYS, state_class=SensorStateClass.MEASUREMENT),
    ]

class MeinVodafoneEntities:
    """Manager."""
    def __init__(self, contract: MeinVodafoneContract):
        self.entities_list = [e for e in create_entities() if e.setup(contract)]