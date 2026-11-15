"""Serve only the optional, bundled Planning card. No data endpoint."""
import json
from pathlib import Path

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.config_entries import ConfigEntryState

from . import DOMAIN

OPTION = "enable_ux"
RESOURCE = "/rhi_planning/frontend/planning-card.js"


class PlanningCardView(HomeAssistantView):
    url = RESOURCE
    name = "rhi_planning:frontend:card"
    # Static JavaScript only. All plan data still requires the admin HA action.
    requires_auth = False

    def __init__(self, hass, payload, version):
        self.hass = hass
        self.payload = payload
        self.headers = {"Cache-Control": "no-store", "X-RHI-Version": version,
                        "X-Content-Type-Options": "nosniff"}

    def _enabled(self):
        entries = self.hass.config_entries.async_entries(DOMAIN)
        return len(entries) == 1 and entries[0].state == ConfigEntryState.LOADED and entries[0].options.get(OPTION) is True

    async def get(self, request):
        if not self._enabled():
            return web.Response(status=404, headers=self.headers)
        return web.Response(body=self.payload, content_type="text/javascript", headers=self.headers)

    async def head(self, request):
        return web.Response(status=200 if self._enabled() else 404,
                            content_type="text/javascript", headers=self.headers)


async def async_register_frontend(hass):
    """One fixed route per HA process; live options gate its availability."""
    if getattr(hass, "http", None) is None:
        return

    def load():
        root = Path(__file__).parent
        return ((root / "frontend" / "planning-card.js").read_bytes(),
                json.loads((root / "manifest.json").read_text())["version"])

    payload, version = await hass.async_add_executor_job(load)
    hass.http.register_view(PlanningCardView(hass, payload, version))
