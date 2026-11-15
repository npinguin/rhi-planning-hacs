"""Native HA pilot entry; existing scheduler remains the sole timer owner."""
DOMAIN = "rhi_planning"



def _validate_config(config):
    from homeassistant.helpers import config_validation as cv
    return cv.config_entry_only_config_schema(DOMAIN)(config)


CONFIG_SCHEMA = _validate_config


async def async_setup(hass, config):
    from .ha_runtime import register_services
    from .frontend import async_register_frontend
    register_services(hass)
    await async_register_frontend(hass)
    return True


async def async_setup_entry(hass, entry):
    from .ha_runtime import Runtime
    entry.runtime_data = Runtime(hass, entry)
    await entry.runtime_data.start()
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    from .frontend import async_setup_ux
    async_setup_ux(hass, entry)
    return True


async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])
