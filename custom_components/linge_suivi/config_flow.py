"""Config flow pour linge_suivi : cree via import YAML uniquement (pas de formulaire utilisateur)."""
from __future__ import annotations

from homeassistant import config_entries

from .const import CONF_SOURCE, DOMAIN


class LingeSuiviConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gere la creation des config entries linge_suivi a partir de la config YAML."""

    VERSION = 1

    async def async_step_import(self, import_config: dict):
        await self.async_set_unique_id(import_config[CONF_SOURCE])
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title=import_config.get("name", import_config[CONF_SOURCE]),
            data=import_config,
        )
