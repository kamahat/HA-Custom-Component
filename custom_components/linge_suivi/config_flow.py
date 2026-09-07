"""Config flow pour linge_suivi : creation via YAML (import) ou via l interface utilisateur."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import CONF_DEVICE_ID, CONF_SOURCE, DOMAIN

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SOURCE): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="binary_sensor")
        ),
        vol.Optional("name"): selector.TextSelector(),
        vol.Optional(CONF_DEVICE_ID): selector.DeviceSelector(),
    }
)


class LingeSuiviConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gere la creation des config entries linge_suivi, via YAML ou l interface."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            source = user_input[CONF_SOURCE]
            await self.async_set_unique_id(source)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input.get("name", source),
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_import(self, import_config: dict):
        await self.async_set_unique_id(import_config[CONF_SOURCE])
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title=import_config.get("name", import_config[CONF_SOURCE]),
            data=import_config,
        )
