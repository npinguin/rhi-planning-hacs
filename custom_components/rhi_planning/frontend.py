"""Serve only the optional, bundled Planning card. No data endpoint."""
import json
import asyncio
import logging
from urllib.parse import urlsplit, parse_qs
from pathlib import Path

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.components import frontend
from homeassistant.core import callback
from homeassistant.config_entries import ConfigEntryState

from . import DOMAIN

OPTION = "enable_ux"
UX_OPTION = OPTION
_LOGGER = logging.getLogger(__name__)
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
        return len(entries) == 1 and entries[0].state == ConfigEntryState.LOADED and entries[0].options.get(OPTION, True) is True

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
    hass.data[f"{DOMAIN}_ux_transport"] = {"version": version, "verified": bool(payload), "file_count": 1}
    hass.http.register_view(PlanningCardView(hass, payload, version))


def ux_diagnostics(hass, entry):
    """Report server-side evidence, never claim a browser rendered the card."""
    transport = hass.data.get(f"{DOMAIN}_ux_transport", {})
    status = hass.data.get(f"{DOMAIN}_ux_lifecycle", {}).get("status", {})
    return {"enabled": entry.options.get(UX_OPTION, True) is True,
            "resource_url": RESOURCE,
            "transport": dict(transport), **status,
            "browser_render_verified": False}


async def reconcile_lovelace(collection, resource, version, enabled):
    """Own only URLs bearing our exact marker; preserve manually added resources."""
    await collection.async_get_info()
    managed, manual = [], []
    for item in collection.async_items():
        try:
            parts = urlsplit(item.get("url", ""))
        except ValueError:
            continue
        if parts.scheme or parts.netloc or parts.path != resource:
            continue
        marker = parse_qs(parts.query).get("rhi_managed")
        if marker == [DOMAIN]:
            managed.append(item)
        else:
            manual.append(item)
    # A manually added canonical resource already provides the card.
    # Never delete or change it, even when the optional UX is disabled.
    manual_modules = [row for row in manual if row.get("type") == "module"]
    if not enabled or manual:
        for row in managed:
            await collection.async_delete_item(row["id"])
        return {"registration": ("manual_resource" if manual_modules else "manual_resource_invalid_type") if enabled and manual else "disabled",
                "resource_count": len(manual), "manual_resource_count": len(manual),
                "duplicate_resource": len(manual) > 1,
                "managed_resource_count": 0}
    expected = f"{resource}?rhi_managed={DOMAIN}&v={version}"
    if managed:
        keep, *duplicates = managed
        if keep["url"] != expected or keep.get("type") != "module":
            await collection.async_update_item(keep["id"], {"url": expected, "res_type": "module"})
        for row in duplicates:
            await collection.async_delete_item(row["id"])
    else:
        await collection.async_create_item({"url": expected, "res_type": "module"})
    return {"registration": "managed_storage", "resource_count": 1,
            "manual_resource_count": 0, "managed_resource_count": 1,
            "duplicate_resource": False}


def async_setup_ux(hass, entry):
    """Register the bundled card through native Lovelace storage; never edit YAML."""
    from homeassistant.components import frontend
    from homeassistant.components.lovelace.const import LOVELACE_DATA
    from homeassistant.config_entries import ConfigEntryState
    from homeassistant.core import callback

    resource = RESOURCE
    lifecycle = hass.data.setdefault(f"{DOMAIN}_ux_lifecycle", {"lock": asyncio.Lock()})
    owned_extra = False
    active = True

    async def reconcile():
        nonlocal owned_extra
        async with lifecycle["lock"]:
            transport = hass.data.get(f"{DOMAIN}_ux_transport", {})
            enabled = (active and entry.state is ConfigEntryState.LOADED
                       and entry.options.get(UX_OPTION, True) is True
                       and transport.get("verified", False))
            lovelace = hass.data.get(LOVELACE_DATA)
            manager = hass.data.get(frontend.DATA_EXTRA_MODULE_URL)
            # Storage mode has one native resource, not a global duplicate.
            try:
                if lovelace is not None and lovelace.resource_mode == "storage":
                    if owned_extra and manager is not None and resource in manager.urls:
                        frontend.remove_extra_js_url(hass, resource)
                    owned_extra = False
                    result = await reconcile_lovelace(lovelace.resources, resource, transport.get("version", ""), enabled)
                    lifecycle["status"] = {"resource_mode": "storage", **result}
                    return
                # YAML belongs to the user. A declared resource takes precedence;
                # otherwise use native extra-module registration, with a diagnostic.
                existing = [] if lovelace is None else [
                    row for row in lovelace.resources.async_items()
                    if row.get("url", "").split("?", 1)[0] == resource and row.get("type") == "module"]
                use_extra = enabled and not existing and manager is not None
                if use_extra and resource not in manager.urls:
                    frontend.add_extra_js_url(hass, resource)
                    owned_extra = True
                elif not use_extra and owned_extra:
                    if manager is not None and resource in manager.urls:
                        frontend.remove_extra_js_url(hass, resource)
                    owned_extra = False
                lifecycle["status"] = {"resource_mode": "yaml" if lovelace else "unavailable",
                                       "registration": ("yaml_declared" if existing else "extra_module_yaml_resource_required") if enabled else "disabled",
                                       "resource_count": len(existing),
                                       "duplicate_resource": len(existing) > 1}
            except Exception as exc:
                lifecycle["status"] = {"registration": "error", "error_type": type(exc).__name__}
                _LOGGER.warning("RHI frontend registration failed: %s", type(exc).__name__)

    @callback
    def sync():
        hass.async_create_task(reconcile())

    async def updated(hass, entry):
        await reconcile()

    @callback
    def cleanup():
        nonlocal active
        active = False
        sync()

    entry.async_on_unload(entry.async_on_state_change(sync))
    entry.async_on_unload(entry.add_update_listener(updated))
    entry.async_on_unload(cleanup)
    sync()
