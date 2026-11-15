"""HA-native pilot readiness entity."""
from homeassistant.components.sensor import SensorEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([PilotStatus(entry)], update_before_add=True)


class PilotStatus(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "RHI Planning pilot status"
    _attr_icon = "mdi:calendar-clock"

    def __init__(self, entry):
        self._attr_unique_id = entry.entry_id + "_pilot_status"
        self.runtime = entry.runtime_data

    async def async_update(self):
        data = self.runtime.status()
        self._attr_native_value = data["state"]
        self._attr_extra_state_attributes = {k:v for k,v in data.items() if k != "state"}
