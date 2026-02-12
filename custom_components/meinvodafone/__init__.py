"""The meinvodafone integration."""

from __future__ import annotations
import asyncio
from datetime import timedelta
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .MeinVodafoneAPIPool import MeinVodafoneAPIPool
from .const import CONTRACT_ID, COORDINATOR, DEFAULT_UPDATE_INTERVAL, DOMAIN, MEINVODAFONE_API_POOL, REQUEST_TIMEOUT
from .MeinVodafoneContract import MeinVodafoneContract
from .MeinVodafoneEntities import MeinVodafoneEntities

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Setup entry."""
    hass.data.setdefault(DOMAIN, {})
    if MEINVODAFONE_API_POOL not in hass.data[DOMAIN]:
        hass.data[DOMAIN][MEINVODAFONE_API_POOL] = MeinVodafoneAPIPool()
    
    coordinator = MeinVodafoneCoordinator(hass, config_entry, timedelta(minutes=DEFAULT_UPDATE_INTERVAL))
    await coordinator.async_refresh()
    hass.data[DOMAIN][config_entry.entry_id] = {COORDINATOR: coordinator}
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

class MeinVodafoneCoordinator(DataUpdateCoordinator):
    """Fetch data from multiple endpoints."""
    def __init__(self, hass, config_entry, update_interval):
        self.config_entry = config_entry
        self.contract_id = config_entry.data.get(CONTRACT_ID)
        self.username = config_entry.data.get(CONF_USERNAME)
        self.password = config_entry.data.get(CONF_PASSWORD)
        self.contract = None
        self.usage_data = {}
        self.tariff_data = {}
        self.entities_list = []
        
        api_pool = hass.data[DOMAIN][MEINVODAFONE_API_POOL]
        self.api = api_pool.get_or_create(self.username, self.password)
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    async def _async_update_data(self) -> MeinVodafoneContract:
        """Fetch all needed data."""
        api_pool = self.hass.data[DOMAIN][MEINVODAFONE_API_POOL]
        if not await api_pool.ensure_authenticated(self.api, self.username):
            raise ConfigEntryAuthFailed()

        async with asyncio.timeout(REQUEST_TIMEOUT):
            # Fetch usage and tariff info in parallel
            usage_task = self.api.get_contract_usage(self.contract_id)
            tariff_task = self.api.get_tariff_details(self.contract_id)
            
            usage_res, tariff_res = await asyncio.gather(usage_task, tariff_task)
            
            if usage_res.get("status_code") != 200:
                raise UpdateFailed(f"Status {usage_res.get('status_code')}")

            self.usage_data = usage_res.get("usage_data", {})
            self.tariff_data = tariff_res
            self.contract = MeinVodafoneContract(self.contract_id, self.usage_data, self.tariff_data)
            
            if not self.entities_list:
                self.entities_list = MeinVodafoneEntities(self.contract).entities_list
            
            return self.contract