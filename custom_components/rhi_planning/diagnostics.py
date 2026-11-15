"""Read-only diagnostics; do not export plan titles or household identifiers."""
import json
from pathlib import Path


async def async_get_config_entry_diagnostics(hass, entry):
    version = await hass.async_add_executor_job(
        lambda: json.loads(Path(__file__).with_name("manifest.json").read_text())["version"])
    status = entry.runtime_data.status()
    from .frontend import ux_diagnostics
    return {"ux": ux_diagnostics(hass, entry), "identity":{"domain":"rhi_planning","version":version},
            "health":status, "configuration":{"mode":"pilot"},
            "build_handoff":{"foundation_required":False},
            "execution":{"physical_writes":False},
            "publication":{"contract":"candidate_v1","cutover_ready":False}}
