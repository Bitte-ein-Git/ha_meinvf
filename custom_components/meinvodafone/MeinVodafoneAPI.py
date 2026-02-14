"""MeinVodafone API."""

import base64
import hashlib
import logging
import secrets
import time
from typing import Any

from aiohttp import ClientError, ClientSession

from .const import (
    API_HOST,
    API_TIMEOUT,
    BILLING,
    CLIENT_ID,
    CURRENT_SUMMARY,
    CYCLE_END,
    CYCLE_START,
    DATA,
    DATA_VALID_UNTIL,
    HEADER_REFERER,
    LAST_SUMMARY,
    LAST_UPDATE,
    MINT_HOST,
    MINUTES,
    NAME,
    NEXT_CYCLE_START,
    PLAN_NAME,
    PLAN_PRICE,
    REMAINING,
    SMS,
    TOTAL,
    USED,
    USER_AGENT,
    X_VF_CLIENT_ID,
)

_LOGGER = logging.getLogger(__name__)


class MeinVodafoneAPI:
    """Main API interaction class."""

    def __init__(self, username: str, password: str) -> None:
        """Initialize session."""
        self.username = username
        self.password = password
        self.session = ClientSession()
        self.is_authenticated = False

    def _generate_code_verifier(self) -> str:
        """PKCE verifier."""
        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz-._~"
        return "".join(secrets.choice(chars) for _ in range(43))

    def _generate_code_challenge(self, code_verifier: str) -> str:
        """PKCE challenge."""
        sha256_hash = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        base64_encoded = base64.b64encode(sha256_hash).decode("utf-8")
        return base64_encoded.replace("+", "-").replace("/", "_").replace("=", "")

    async def close(self) -> None:
        """Close connection."""
        if self.session:
            await self.session.close()
        self.is_authenticated = False

    async def login(self) -> bool:
        """Handle login flow."""
        try:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)

            authorize_url = (
                f"{MINT_HOST}/oidc/authorize?response_type=code&client_id={CLIENT_ID}"
                f"&scope=openid%20profile%20validate-token%20offline_access%20webseal"
                f"&redirect_uri=mvapp://oidclogin&code_challenge={code_challenge}"
                f"&code_challenge_method=S256&prompt=none"
            )

            async with self.session.get(authorize_url, headers={"User-Agent": USER_AGENT}, timeout=API_TIMEOUT, allow_redirects=False) as response:
                if response.status not in (200, 302):
                    return False

            payload = {"authnIdentifier": self.username, "credential": self.password}
            url = f"{MINT_HOST}/rest/v60/session/start"
            async with self.session.post(url, headers={"User-Agent": USER_AGENT}, json=payload, timeout=API_TIMEOUT) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("userId"):
                        self.is_authenticated = True
                        return True
                return False
        except Exception as error:
            _LOGGER.error("Login failed: %s", error)
            return False

    async def get_contracts(self) -> list[str]:
        """Fetch mobile contracts."""
        contracts = []
        timestamp = f"{int(time.time())}"
        try:
            url = f"{API_HOST}/vluxgate/vlux/hashing"
            headers = {"Referer": HEADER_REFERER, "User-Agent": USER_AGENT, "X-Vf-Api": timestamp, "X-Vf-Clientid": X_VF_CLIENT_ID}
            async with self.session.get(url, headers=headers, timeout=API_TIMEOUT) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for contract in data.get("hashedIds", []):
                        if contract.get("type") == "mobile" and contract.get("id"):
                            contracts.append(contract.get("id"))
        except Exception as error:
            _LOGGER.error("Contract fetch error: %s", error)
        return contracts

    async def get_tariff_details(self, contract_number: str) -> dict[str, Any]:
        """Fetch future month info (API 1)."""
        tariff_data = {PLAN_PRICE: None, NEXT_CYCLE_START: None}
        timestamp = f"{int(time.time())}"
        try:
            url = f"{API_HOST}/vluxgate/vlux/mobile/tariffBooked/{contract_number}?market-code=MMO"
            headers = {"Referer": HEADER_REFERER, "User-Agent": USER_AGENT, "X-Vf-Api": timestamp, "X-Vf-Clientid": X_VF_CLIENT_ID}
            async with self.session.get(url, headers=headers, timeout=API_TIMEOUT) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    subs = data.get("subscriptionVBO", [{}])[0].get("subscriptions", [{}])
                    details = subs[0].get("customerProduct", {}).get("tariffDetails", {})
                    
                    tariff_data[NEXT_CYCLE_START] = details.get("cycleStartDate")
                    
                    price = details.get("price")
                    unit = details.get("unitOfMeasure")
                    if price:
                        currency = "€" if unit == "EUR" else unit
                        tariff_data[PLAN_PRICE] = f"{str(price).replace('.', ',')}{currency}"
        except Exception:
            _LOGGER.error("Tariff details fetch error")
        return tariff_data

    async def get_contract_usage(self, contract_number: str) -> dict[str, Any]:
        """Fetch current month usage and plan name (API 2)."""
        usage_data = {BILLING: {}, MINUTES: [], SMS: [], DATA: [], DATA_VALID_UNTIL: None, PLAN_NAME: None}
        timestamp = f"{int(time.time())}"
        try:
            url = f"{API_HOST}/vluxgate/vlux/mobile/unbilledUsage/{contract_number}?subscrType=UCM"
            headers = {"Referer": HEADER_REFERER, "User-Agent": USER_AGENT, "X-Vf-Api": timestamp, "X-Vf-Clientid": X_VF_CLIENT_ID}
            
            mapping = {
                "daten": DATA, "d_eu_data": DATA,
                "minuten": MINUTES, "d_eu_flat_allnet_units": MINUTES,
                "sms": SMS, "d_int_units": SMS
            }

            async with self.session.get(url, headers=headers, timeout=API_TIMEOUT) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    vbo = data.get("serviceUsageVBO", {})
                    
                    # Plan name from current month API
                    acc_details = vbo.get("usageAccounts", [{}])[0]
                    usage_data[PLAN_NAME] = acc_details.get("productSpecification", {}).get("tariffDetails", {}).get("name")

                    bill = vbo.get("billDetails", {})
                    if bill:
                        usage_data[BILLING] = {
                            CURRENT_SUMMARY: bill.get("currentSummary", {}).get("amount"),
                            LAST_SUMMARY: bill.get("lastSummary", {}).get("amount"),
                            CYCLE_START: bill.get("billCycleStartDate"),
                            CYCLE_END: bill.get("billCycleEndDate"),
                        }

                    for account in vbo.get("usageAccounts", []):
                        for group in account.get("usageGroup", []):
                            target = mapping.get(group.get("container", "").lower())
                            if target:
                                agg = group.get("vluxgateAgg", {})
                                usage_list = group.get("usage", [{}])
                                usage_item = usage_list[0] if usage_list else {}
                                
                                if target == DATA and usage_item and not usage_data[DATA_VALID_UNTIL]:
                                    usage_data[DATA_VALID_UNTIL] = usage_item.get("endDate")

                                item = {
                                    NAME: agg.get("name") or usage_item.get("name"),
                                    REMAINING: agg.get("aggregateRemaining") if agg.get("aggregateRemaining") is not None else usage_item.get("remaining"),
                                    USED: agg.get("aggregateUsed") if agg.get("aggregateUsed") is not None else usage_item.get("used"),
                                    TOTAL: agg.get("aggregateTotal") if agg.get("aggregateTotal") is not None else usage_item.get("total"),
                                    LAST_UPDATE: usage_item.get("lastUpdateDate"),
                                }
                                usage_data[target].append(item)
                    return {"status_code": 200, "usage_data": usage_data}
                return {"status_code": resp.status}
        except Exception as error:
            _LOGGER.error("Usage fetch error: %s", error)
            return {"status_code": None, "error_message": str(error)}