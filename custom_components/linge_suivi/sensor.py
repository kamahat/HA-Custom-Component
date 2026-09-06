"""Durée du dernier cycle détectée via un binary_sensor de marche, avec historique persistant."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON, STATE_OFF, UnitOfTime
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import CONF_DEVICE_ID, CONF_SOURCE, DOMAIN

_LOGGER = logging.getLogger(__name__)

STORAGE_VERSION = 1
MAX_HISTORY = 200


def slugify_source(source: str) -> str:
    return source.replace(".", "_")


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    source = entry.data[CONF_SOURCE]
    device_id = entry.data.get(CONF_DEVICE_ID)

    device_info = None
    if device_id:
        dev_reg = dr.async_get(hass)
        device = dev_reg.async_get(device_id)
        if device:
            device_info = {
                "identifiers": device.identifiers,
                "connections": device.connections,
            }
        else:
            _LOGGER.warning(
                "linge_suivi: device_id %s introuvable dans le registre pour %s",
                device_id,
                entry.title,
            )

    store = Store(hass, STORAGE_VERSION, f"{DOMAIN}_{slugify_source(source)}")
    async_add_entities([LingeCycleSensor(source, device_info, store)])


class LingeCycleSensor(SensorEntity):
    """Durée du dernier cycle détecté sur un binary_sensor marche/arrêt, avec historique persistant."""

    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_name = "Dernière durée de cycle"
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:history"

    def __init__(self, source: str, device_info, store: Store) -> None:
        self._source = source
        self._attr_unique_id = f"{DOMAIN}_{slugify_source(source)}_derniere_duree"
        if device_info is not None:
            self._attr_device_info = device_info
        self._store = store
        self._history: list = []
        self._current_start: str | None = None
        self._attr_native_value = None

    async def async_added_to_hass(self) -> None:
        data = await self._store.async_load()
        if data:
            self._history = data.get("cycles", [])
            self._current_start = data.get("current_start")
            if self._history:
                self._attr_native_value = self._history[-1]["duree_min"]

        # Cycle déjà en cours au démarrage de HA (état déjà on) sans départ connu :
        # on prend maintenant comme départ, ce qui sous-estime uniquement ce premier cycle.
        current_state = self.hass.states.get(self._source)
        if current_state and current_state.state == STATE_ON and self._current_start is None:
            self._current_start = dt_util.utcnow().isoformat()
            await self._save()

        self.async_on_remove(
            async_track_state_change_event(
                self.hass, [self._source], self._handle_state_change
            )
        )

    @callback
    def _handle_state_change(self, event: Event) -> None:
        old_state = event.data.get("old_state")
        new_state = event.data.get("new_state")
        if new_state is None:
            return

        if new_state.state == STATE_ON and (old_state is None or old_state.state != STATE_ON):
            self._current_start = dt_util.utcnow().isoformat()
            self.hass.async_create_task(self._save())
            return

        if new_state.state == STATE_OFF and self._current_start is not None:
            start = dt_util.parse_datetime(self._current_start)
            end = dt_util.utcnow()
            duration_s = (end - start).total_seconds()
            record = {
                "debut": self._current_start,
                "fin": end.isoformat(),
                "duree_min": round(duration_s / 60, 1),
                "duree_s": round(duration_s),
            }
            self._history.append(record)
            self._history = self._history[-MAX_HISTORY:]
            self._current_start = None
            self._attr_native_value = record["duree_min"]
            self.hass.async_create_task(self._save())
            self.async_write_ha_state()

    async def _save(self) -> None:
        await self._store.async_save(
            {
                "cycles": self._history,
                "current_start": self._current_start,
            }
        )

    @property
    def extra_state_attributes(self):
        last = self._history[-1] if self._history else None
        return {
            "debut_dernier_cycle": last["debut"] if last else None,
            "fin_dernier_cycle": last["fin"] if last else None,
            "nombre_cycles": len(self._history),
            "historique": self._history,
        }
