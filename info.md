<div align="center">
  <img src="https://github.com/Bitte-ein-Git/ha_meinvf/blob/dev/images/vf.png" alt="VF Icon" width="256">
</div>

</br></br>

{% if not installed %}

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

[![ADD][hacs2]](https://ha-link.heyfordy.dev/redirect/hacs_repository/?owner=Bitte-ein-Git&repository=ha_meinvf&category=integration)

## Installation (Manual)
1. Add this Repository to HACS:
   - HACS > 3 dots > "Add custom repository"
   - URL: `Bitte-ein-Git/ha_meinvf`
   - Type: Integration

2. Select "**📶• MeinVF**".

<hr>

{% endif %}

{% if installed and not configured %}

## Configuration

> [!CAUTION]
> After installation you **have to restart Home Assistant**

### Easy Configuration (Link to Config Screen)
[![ADD][setup2]](https://ha-link.heyfordy.dev/redirect/config_flow_start/?domain=meinvodafone)
### Manual Configuration
1. Add a new config entry via UI:
   - Go to your Home Assistant **Settings**
   - Select "**Devices & services**"
   - At the bottom right select "**+ Add integration**"

2. Select "**📶• MeinVF**".

{% endif %}

<hr>

[![HACS][hacsbadge]](https://hacs.xyz)

# License

[Apache-2.0](LICENSE). By providing a contribution, you agree the contribution is licensed under Apache-2.0. This is required for Home Assistant contributions.

[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
[hacs1]: https://img.shields.io/badge/HACS-%23ff8c00.svg?style=for-the-badge&logo=homeassistantcommunitystore&label=Add%20Repository%20to
[hacs2]: https://ha-link.heyfordy.dev/badges/hacs_repository.svg
[setup1]: https://img.shields.io/badge/HA-%2318BCF2.svg?style=for-the-badge&logo=homeassistant&label=Add%20Integration%20to
[setup2]: https://ha-link.heyfordy.dev/badges/config_flow_start.svg