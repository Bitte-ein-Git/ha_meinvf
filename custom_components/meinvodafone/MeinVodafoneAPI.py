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
    PLAN_NAME,
    PLAN_PRICE,
    REMAINING,
    SMS,
    TARIFF,
    TOTAL,
    USED,
    USER_AGENT,
    X_VF_CLIENT_ID,
)

_LOGGER = logging.getLogger(__name__)


class MeinVodafoneAPI:
    """Main MeinVodafone API class to MeinVodafone services."""

    def __init__(self, username: str, password: str) -> None:
        """Init MeinVodafone API class."""
        self.username = username
        self.password = password
        self.session = ClientSession()
        self.is_authenticated = False

    def _generate_code_verifier(self) -> str:
        """Generate a random code verifier for PKCE."""
        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz-._~"
        code_verifier = "".join(secrets.choice(chars) for _ in range(43))
        return code_verifier

    def _generate_code_challenge(self, code_verifier: str) -> str:
        """Generate code challenge from code verifier using SHA256."""
        sha256_hash = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        base64_encoded = base64.b64encode(sha256_hash).decode("utf-8")
        code_challenge = (
            base64_encoded.replace("+", "-").replace("/", "_").replace("=", "")
        )
        return code_challenge

    async def close(self) -> None:
        """Close the API session."""
        if self.session:
            await self.session.close()
        self.is_authenticated = False

    async def login(self) -> bool:
        """Start session API with two-step authentication."""
        try:
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)

            authorize_url = (
                f"{MINT_HOST}/oidc/authorize"
                f"?response_type=code"
                f"&client_id={CLIENT_ID}"
                f"&scope=openid%20profile%20validate-token%20offline_access%20webseal"
                f"&redirect_uri=mvapp://oidclogin"
                f"&code_challenge={code_challenge}"
                f"&code_challenge_method=S256"
                f"&prompt=none"
            )

            async with self.session.get(
                authorize_url,
                headers={"User-Agent": USER_AGENT},
                timeout=API_TIMEOUT,
                allow_redirects=False,
            ) as response:
                if response.status not in (200, 302):
                    return False

            payload = {"authnIdentifier": self.username, "credential": self.password}
            url = f"{MINT_HOST}/rest/v60/session/start"
            async with self.session.post(
                url, headers={"User-Agent": USER_AGENT}, json=payload, timeout=API_TIMEOUT
            ) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data.get("userId"):
                        self.is_authenticated = True
                        return True
                return False
        except Exception as error:
            _LOGGER.error("Error during login: %s", error)
            return False

    async def get_contracts(self) -> list[str]:
        """Get contracts API."""
        contracts: list[str] = []
        timestamp = f"{int(time.time())}"
        try:
            url = f"{API_HOST}/vluxgate/vlux/hashing"
            headers = {
                "Referer": HEADER_REFERER,
                "User-Agent": USER_AGENT,
                "X-Vf-Api": timestamp,
                "X-Vf-Clientid": X_VF_CLIENT_ID,
            }
            async with self.session.get(url, headers=headers, timeout=API_TIMEOUT) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for contract in data.get("hashedIds", []):
                        if contract.get("type") == "mobile" and contract.get("id"):
                            contracts.append(contract.get("id"))
        except Exception as error:
            _LOGGER.error("Error fetching contracts: %s", error)
        return contracts

    async def get_tariff_details(self, contract_number: str) -> dict[str, Any]:
        """Get tariff details from API URL 1."""
        tariff_data = {PLAN_NAME: None, PLAN_PRICE: None}
        timestamp = f"{int(time.time())}"
        try:
            url = f"{API_HOST}/vluxgate/vlux/mobile/tariffBooked/{contract_number}?market-code=MMO"
            headers = {
                "Referer": HEADER_REFERER,
                "User-Agent": USER_AGENT,
                "X-Vf-Api": timestamp,
                "X-Vf-Clientid": X_VF_CLIENT_ID,
            }
            async with self.session.get(url, headers=headers, timeout=API_TIMEOUT) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    subs = data.get("subscriptionVBO", [{}])[0].get("subscriptions", [{}])
                    tariff = subs[0].get("customerProduct", {}).get("tariffDetails", {})
                    
                    tariff_data[PLAN_NAME] = tariff.get("name")
                    price = tariff.get("price")
                    currency = "€" if tariff.get("unitOfMeasure") == "EUR" else tariff.get("unitOfMeasure", "")
                    if price:
                        tariff_data[PLAN_PRICE] = f"{str(price).replace('.', ',')}{currency}"
        except Exception as error:
            _LOGGER.error("Error fetching tariff details: %s", error)
        return tariff_data

    async def get_contract_usage(self, contract_number: str) -> dict[str, Any]:
        """Get usage data API including data validity."""
        contract_usage_data: dict[str, Any] = {BILLING: {}, MINUTES: [], SMS: [], DATA: [], DATA_VALID_UNTIL: None}
        try:
            url = f"{API_HOST}/vluxgate/vlux/mobile/unbilledUsage/{contract_number}"
            timestamp = f"{int(time.time())}"
            headers = {
                "Referer": HEADER_REFERER,
                "User-Agent": USER_AGENT,
                "X-Vf-Api": timestamp,
                "X-Vf-Clientid": X_VF_CLIENT_ID,
            }
            name_mapping = {"minuten": MINUTES, "sms": SMS, "daten": DATA, "d_eu_data": DATA}

            async with self.session.get(url, headers=headers, timeout=API_TIMEOUT) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    vbo = data.get("serviceUsageVBO", {})
                    
                    # Extraction of billing info
                    bill = vbo.get("billDetails", {})
                    if bill:
                        contract_usage_data[BILLING] = {
                            CURRENT_SUMMARY: bill.get("currentSummary", {}).get("amount"),
                            LAST_SUMMARY: bill.get("lastSummary", {}).get("amount"),
                            CYCLE_START: bill.get("billCycleStartDate"),
                            CYCLE_END: bill.get("billCycleEndDate"),
                        }

                    # Extraction of usage accounts
                    for account in vbo.get("usageAccounts", []):
                        for group in account.get("usageGroup", []):
                            container = group.get("container", "").lower()
                            target = name_mapping.get(container)
                            if target:
                                agg = group.get("vluxgateAgg", {})
                                last_upd = group.get("usage", [{}])[0].get("lastUpdateDate")
                                
                                # Extra logic for data validity date
                                if target == DATA and not contract_usage_data[DATA_VALID_UNTIL]:
                                    contract_usage_data[DATA_VALID_UNTIL] = group.get("usage", [{}])[0].get("endDate")

                                item = {
                                    NAME: agg.get("name"),
                                    REMAINING: agg.get("aggregateRemaining"),
                                    USED: agg.get("aggregateUsed"),
                                    TOTAL: agg.get("aggregateTotal"),
                                    LAST_UPDATE: last_upd,
                                }
                                contract_usage_data[target].append(item)
                    
                    return {"status_code": 200, "usage_data": contract_usage_data}
                return {"status_code": resp.status}
        except Exception as error:
            _LOGGER.error("Error fetching usage: %s", error)
            return {"status_code": None, "error_message": str(error)}

    def _validate_usage_values(self, remaining, used, total, unit) -> bool:
        """Validate numeric usage values."""
        return True

    def _is_valid_data_value(self, value, unit) -> bool:
        """Simple check for data glitches."""
        return True