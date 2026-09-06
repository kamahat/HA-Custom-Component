"""Linge - Suivi cycles : duree du dernier cycle + historique persistant."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import CONF_DEVICE_ID, CONF_SOURCE, DOMAIN

PLATFORMS = ["sensor"]

APPLIANCE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SOURCE): cv.entity_id,
        vol.Optional("name"): cv.string,
        vol.Optional(CONF_DEVICE_ID): cv.string,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: {cv.slug: APPLIANCE_SCHEMA}},
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    domain_conf = config.get(DOMAIN)
    if domain_conf:
        for key, conf in domain_conf.items():
            conf = dict(conf)
            conf.setdefault("name", key)
            hass.async_create_task(
                hass.config_entries.flow.async_init(
                    DOMAIN, context={"source": "import"}, data=conf
                )
            )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
