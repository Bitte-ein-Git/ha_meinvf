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

ISO_DATE_FORMAT = "%Y-%m-%d"


class MeinVodafoneContract:
    """Helper class to process and sum usage data."""

    def __init__(self, contract_id: str, usage_data: dict, tariff_data: dict = None) -> None:
        """Initialize contract processing."""
        self.contract_id = contract_id
        self.usage_data = usage_data
        self.tariff_data = tariff_data or {}

    def get_value(self, container: str, key: str) -> str | None:
        """Return summarized string value for a usage category."""
        items = self.usage_data.get(container, [])
        if not items:
            return None
        
        if key == NAME:
            return ", ".join([str(i.get(key, "")) for i in items if i.get(key)])
        if key == LAST_UPDATE:
            dates = [i.get(key) for i in items if i.get(key)]
            return max(dates) if dates else None

        # Numeric summation
        total_sum = 0
        found = False
        for i in items:
            val = i.get(key)
            if val is not None:
                try:
                    total_sum += int(val)
                    found = True
                except (ValueError, TypeError):
                    continue
        return str(total_sum) if found else None

    @property
    def plan_name(self) -> str | None: return self.tariff_data.get(PLAN_NAME)
    @property
    def is_plan_name_supported(self) -> bool: return self.plan_name is not None

    @property
    def plan_price(self) -> str | None: return self.tariff_data.get(PLAN_PRICE)
    @property
    def is_plan_price_supported(self) -> bool: return self.plan_price is not None

    @property
    def data_available_until(self) -> datetime.date | None:
        """Return end date of current data volume as date object."""
        val = self.usage_data.get(DATA_VALID_UNTIL)
        if not val:
            return None
        try:
            # Parse YYYY-MM-DD
            return datetime.date.fromisoformat(str(val)[:10])
        except (ValueError, TypeError):
            return None

    @property
    def is_data_available_until_supported(self) -> bool:
        return self.data_available_until is not None

    # Minutes
    @property
    def minutes_remaining(self) -> str | None: return self.get_value(MINUTES, REMAINING)
    @property
    def is_minutes_remaining_supported(self) -> bool: return self.minutes_remaining is not None
    @property
    def minutes_used(self) -> str | None: return self.get_value(MINUTES, USED)
    @property
    def is_minutes_used_supported(self) -> bool: return self.minutes_used is not None
    @property
    def minutes_total(self) -> str | None: return self.get_value(MINUTES, TOTAL)
    @property
    def is_minutes_total_supported(self) -> bool: return self.minutes_total is not None

    # SMS
    @property
    def sms_remaining(self) -> str | None: return self.get_value(SMS, REMAINING)
    @property
    def is_sms_remaining_supported(self) -> bool: return self.sms_remaining is not None
    @property
    def sms_used(self) -> str | None: return self.get_value(SMS, USED)
    @property
    def is_sms_used_supported(self) -> bool: return self.sms_used is not None
    @property
    def sms_total(self) -> str | None: return self.get_value(SMS, TOTAL)
    @property
    def is_sms_total_supported(self) -> bool: return self.sms_total is not None

    # Data
    @property
    def data_remaining(self) -> str | None: return self.get_value(DATA, REMAINING)
    @property
    def is_data_remaining_supported(self) -> bool: return self.data_remaining is not None
    @property
    def data_used(self) -> str | None: return self.get_value(DATA, USED)
    @property
    def is_data_used_supported(self) -> bool: return self.data_used is not None
    @property
    def data_total(self) -> str | None: return self.get_value(DATA, TOTAL)
    @property
    def is_data_total_supported(self) -> bool: return self.data_total is not None

    # Billing and Cycle
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
        """Calculate days left in cycle (with fallback to tariff data)."""
        # Try billing data first, then tariff details
        end = self.usage_data.get(BILLING, {}).get(CYCLE_END) or self.tariff_data.get(CYCLE_END)
        if not end:
            return None
        try:
            now = datetime.datetime.now(datetime.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = datetime.datetime.strptime(str(end)[:10], ISO_DATE_FORMAT).replace(tzinfo=datetime.timezone.utc)
            return (end_date - now).days
        except Exception:
            return None

    @property
    def is_billing_cycle_days_supported(self) -> bool:
        return self.billing_cycle_days is not None