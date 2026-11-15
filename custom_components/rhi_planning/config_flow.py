"""Single confirmation; discovery is not a commissioning wizard."""
import probatio as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .frontend import OPTION
from . import DOMAIN


class RHIConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return RHIOptionsFlow()

    async def async_step_user(self, user_input=None):
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        if user_input is not None:
            return self.async_create_entry(title="RHI Planning", data={})
        return self.async_show_form(step_id="user", data_schema=vol.Schema({}))


class RHIOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data={**self.config_entry.options, **user_input})
        return self.async_show_form(step_id="init", data_schema=vol.Schema({
            vol.Required(OPTION, default=self.config_entry.options.get(OPTION, True)): bool,
        }))
