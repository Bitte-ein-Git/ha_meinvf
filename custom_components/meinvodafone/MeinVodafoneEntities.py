"""MeinVodafone Entities."""

import logging
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.components.sensor.const import UnitOfTime
from homeassistant.const import CURRENCY_EURO
from homeassistant.helpers.entity import EntityCategory
from .MeinVodafoneContract import MeinVodafoneContract

_LOGGER = logging.getLogger(__name__)

class BaseEntity:
    """Base class for components."""
    def __init__(self, component, attr, name, icon=None, plan_name=None, entity_type=None, device_class=None, state_class=None, display_precision=None):
        self.attr = attr
        self.component = component
        self.name = name
        self.icon = icon
        self.plan_name = plan_name
        self.entity_type = entity_type
        self.device_class = device_class
        self.state_class = state_class
        self.display_precision = display_precision
        self.contract = None

    def setup(self, contract) -> bool:
        self.contract = contract
        supp_attr = f"is_{self.attr}_supported"
        return getattr(self.contract, supp_attr, False)

class Sensor(BaseEntity):
    """Sensor entity definition."""
    def __init__(self, attr, name, icon, unit, plan_name=None, entity_type=None, device_class=None, state_class=None, display_precision=None):
        super().__init__("sensor", attr, name, icon, plan_name, entity_type, device_class, state_class, display_precision)
        self.unit = unit

def create_entities() -> list[Sensor]:
    """Return entity list."""
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
        Sensor("billing_cycle_days", "Billing cycle days", "mdi:credit-card-sync", UnitOfTime.DAYS, state_class=SensorStateClass.MEASUREMENT),
    ]

class MeinVodafoneEntities:
    """Access class."""
    def __init__(self, contract: MeinVodafoneContract):
        self.entities_list = [e for e in create_entities() if e.setup(contract)]