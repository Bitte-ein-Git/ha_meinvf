<div align="center">
  <img src="https://github.com/Bitte-ein-Git/ha_meinvf/blob/dev/images/vf.png" alt="VF Icon" width="256">
</div>

</br></br>

<div id="toc">
  <ul align="center" style="list-style: none">
    <summary>
      <h1 style="border-bottom: 0; display: inline-block;">
        <b>📶• MeinVF</b></br>
          <sub><i><u>Home Assistant Integration</i> 🏡</u></sub></h1>
    </summary>
  </ul>
</div>

</br>

## Installation (Easy)
> [!NOTE]
> You may need to enter your Home Assistant URL/IP address first.

### Simply use this button to automatically navigate to the HACS repository in your Home Assistant!

[![ADD][hacs2]](https://ha-link.heyfordy.de/redirect/hacs_repository/?owner=Bitte-ein-Git&repository=ha_meinvf&category=integration)

## Installation (Manual)
1. Add this Repository to HACS:
   - HACS > 3 dots > "Add custom repository"
   - URL: `Bitte-ein-Git/ha_meinvf`
   - Type: Integration

2. Select "**📶• MeinVF**".

<hr>

## Configuration

> [!CAUTION]
> After installation you **have to restart Home Assistant**

### Easy Configuration (Link to Config Screen)
[![ADD][setup2]](https://ha-link.heyfordy.de/redirect/config_flow_start/?domain=meinvodafone)
### Manual Configuration
1. Add a new config entry via UI:
   - Go to your Home Assistant **Settings**
   - Select "**Devices & services**"
   - At the bottom right select "**+ Add integration**"

2. Select "**📶• MeinVF**".

### 3. Setup the Integration

1. Go to Settings -> Devices & Services
2. Shift reload your browser
3. Click Add Integration

4. Search for MeinVF<br />
![find_integration](images/find_integration.png)

5. Enter your username and password, press submit<br />
![enter_user_pass](images/enter_user_pass.png)

6. Select contract and press submit<br />
![select_contract](images/select_contract.png)

7. If you see this screen, your configuration is successful<br />
![config_success](images/config_success.png)

---

## IMPORTANT
- The retry mechanism has intentionally been omitted due to the sensitivity of the Vodafone servers.
- Multiple retries could result in a 24-hour block. 
- The data usage retrieval period is configured for every 15 minutes.
- Support for 2FA (two-factor authentication) is currently unavailable.
- If you're on a flat tariff, both your Total and Remaining sensors will display as 0.

---

## Functionality
- Minutes Used/Remaining/Total
- SMS Used/Remaining/Total
- Data Used/Remaining/Total
- Support for multiple plans.
- Billing Summary Current/Previous.
- Billing Cycle (days left)

![sensors_screenshot](images/sensors_screenshot.png)

<hr>

[![HACS][hacsbadge]](https://hacs.xyz)

# License

[Apache-2.0](LICENSE). By providing a contribution, you agree the contribution is licensed under Apache-2.0. This is required for Home Assistant contributions.

[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
[hacs1]: https://img.shields.io/badge/HACS-%23ff8c00.svg?style=for-the-badge&logo=homeassistantcommunitystore&label=Add%20Repository%20to
[hacs2]: https://ha-link.heyfordy.de/badges/hacs_repository.svg
[setup1]: https://img.shields.io/badge/HA-%2318BCF2.svg?style=for-the-badge&logo=homeassistant&label=Add%20Integration%20to
[setup2]: https://ha-link.heyfordy.de/badges/config_flow_start.svg