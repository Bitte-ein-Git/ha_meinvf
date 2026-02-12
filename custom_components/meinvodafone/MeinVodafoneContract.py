"""MeinVodafone Contract."""

import datetime
import logging
from typing import Any

from .const import (
    BILLING,
    CURRENT_SUMMARY,
    CYCLE_END,
    CYCLE_START,
    DATA,
    DATA_VALID_UNTIL,
    LAST_SUMMARY,
    LAST_UPDATE,
    MINUTES,
    NAME,
    PLAN_NAME,
    PLAN_PRICE,
    REMAINING,
    SMS,
    TOTAL,
    USED,
)

_LOGGER = logging.getLogger(__name__)

ISO_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
ISO_DATE_FORMAT = "%Y-%m-%d"


class MeinVodafoneContract:
    """Contract data processing class."""

    def __init__(self, contract_id: str, usage_data: dict[str, Any], tariff_data: dict[str, Any] = None) -> None:
        """Initialize contract."""
        self.contract_id = contract_id
        self.usage_data = usage_data
        self.tariff_data = tariff_data or {}

    def get_value(self, container: str, key: str | None = None) -> str | None:
        """Summarize usage data."""
        data_list = self.usage_data.get(container, [])
        if not data_list:
            return None

        if key == NAME:
            return ", ".join([i.get(key, "") for i in data_list if i.get(key)])
        if key == LAST_UPDATE:
            updates = [i.get(key) for i in data_list if i.get(key)]
            return max(updates) if updates else datetime.datetime.now().isoformat()
        
        return str(sum(int(i.get(key, 0)) for i in data_list if i.get(key) is not None))

    # General properties
    @property
    def plan_name(self) -> str | None:
        """Return the tariff name."""
        return self.tariff_data.get(PLAN_NAME)

    @property
    def is_plan_name_supported(self) -> bool:
        """Check support for plan name."""
        return self.plan_name is not None

    @property
    def plan_price(self) -> str | None:
        """Return the plan price."""
        return self.tariff_data.get(PLAN_PRICE)

    @property
    def is_plan_price_supported(self) -> bool:
        """Check support for plan price."""
        return self.plan_price is not None

    @property
    def data_available_until(self) -> str | None:
        """Return the end date of current data volume."""
        return self.usage_data.get(DATA_VALID_UNTIL)

    @property
    def is_data_available_until_supported(self) -> bool:
        """Check support for data validity date."""
        return self.data_available_until is not None

    # Usage properties (Minutes/SMS)
    @property
    def minutes_remaining(self) -> str | None: return self.get_value(MINUTES, REMAINING)
    @property
    def is_minutes_remaining_supported(self) -> bool: return bool(self.minutes_remaining)
    @property
    def minutes_used(self) -> str | None: return self.get_value(MINUTES, USED)
    @property
    def is_minutes_used_supported(self) -> bool: return bool(self.minutes_used)
    @property
    def minutes_total(self) -> str | None: return self.get_value(MINUTES, TOTAL)
    @property
    def is_minutes_total_supported(self) -> bool: return bool(self.minutes_total)

    @property
    def sms_remaining(self) -> str | None: return self.get_value(SMS, REMAINING)
    @property
    def is_sms_remaining_supported(self) -> bool: return bool(self.sms_remaining)
    @property
    def sms_used(self) -> str | None: return self.get_value(SMS, USED)
    @property
    def is_sms_used_supported(self) -> bool: return bool(self.sms_used)
    @property
    def sms_total(self) -> str | None: return self.get_value(SMS, TOTAL)
    @property
    def is_sms_total_supported(self) -> bool: return bool(self.sms_total)

    # Data properties
    @property
    def data_remaining(self) -> str | None: return self.get_value(DATA, REMAINING)
    @property
    def is_data_remaining_supported(self) -> bool: return bool(self.data_remaining)
    @property
    def data_used(self) -> str | None: return self.get_value(DATA, USED)
    @property
    def is_data_used_supported(self) -> bool: return bool(self.data_used)
    @property
    def data_total(self) -> str | None: return self.get_value(DATA, TOTAL)
    @property
    def is_data_total_supported(self) -> bool: return bool(self.data_total)

    # Billing properties
    @property
    def billing_current_summary(self) -> str | None: return self.usage_data.get(BILLING, {}).get(CURRENT_SUMMARY)
    @property
    def is_billing_current_summary_supported(self) -> bool: return self.billing_current_summary is not None
    @property
    def billing_last_summary(self) -> str | None: return self.usage_data.get(BILLING, {}).get(LAST_SUMMARY)
    @property
    def is_billing_last_summary_supported(self) -> bool: return self.billing_last_summary is not None

    @property
    def billing_cycle_days(self) -> int | None:
        """Calculate days left in cycle."""
        end_date = self.usage_data.get(BILLING, {}).get(CYCLE_END)
        if not end_date: return None
        try:
            today = datetime.datetime.now(datetime.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            end = datetime.datetime.strptime(end_date, ISO_DATE_FORMAT).replace(tzinfo=datetime.timezone.utc)
            return (end - today).days
        except: return None

    @property
    def is_billing_cycle_days_supported(self) -> bool:
        return self.usage_data.get(BILLING, {}).get(CYCLE_END) is not None