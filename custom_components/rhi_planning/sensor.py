"""HA-native pilot readiness entity."""
from datetime import datetime
from zoneinfo import ZoneInfo
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import TrackStates, async_track_state_change_filtered
from .model import activity_publication


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([PilotStatus(entry)], update_before_add=True)


class PilotStatus(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "RHI Planning pilot status"
    _attr_icon = "mdi:calendar-clock"

    def __init__(self, entry):
        self._attr_unique_id = entry.entry_id + "_pilot_status"
        self.runtime = entry.runtime_data
        self._source_revision = 0

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        tracker = async_track_state_change_filtered(
            self.hass, TrackStates(False, set(), {"sensor", "switch"}), self._source_changed)
        self.async_on_remove(tracker.async_remove)
        self.async_on_remove(self.hass.bus.async_listen(er.EVENT_ENTITY_REGISTRY_UPDATED, self._registry_changed))

    @callback
    def _source_changed(self, event):
        entity_id = event.data["entity_id"]
        if entity_id == self.entity_id:
            return
        item = er.async_get(self.hass).async_get(entity_id)
        states = (event.data.get("old_state"), event.data.get("new_state"))
        if ((item and item.platform == "scheduler" and item.domain == "switch")
                or (item and item.domain == "sensor" and any(
                    state and activity_publication(state.attributes,item.platform,item.unique_id)
                    for state in states))):
            self._invalidate()

    @callback
    def _registry_changed(self, event):
        # Registration, removal and rename can change native source evidence
        # even when counts stay identical. No source registry is copied.
        if event.data.get("entity_id") != self.entity_id:
            self._invalidate()

    @callback
    def _invalidate(self):
        self._source_revision += 1
        self.async_schedule_update_ha_state(force_refresh=True)

    async def async_update(self):
        data = self.runtime.status()
        self._attr_native_value = data["state"]
        self._attr_extra_state_attributes = {k:v for k,v in data.items() if k != "state"}
        self._attr_extra_state_attributes.update(
            source_revision=self._source_revision,
            calendar_date=datetime.now(ZoneInfo(self.hass.config.time_zone)).date().isoformat())
