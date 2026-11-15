# RHI Planning

Unified native Scheduler overview, guarded enable/pause, approved device selection and optional integrated Planning card using the existing Scheduler Card.

## Installation

1. Add `https://github.com/npinguin/rhi-planning-hacs` as a custom Integration repository in HACS. Enable prereleases and select the published TEST version.
2. Back up Home Assistant, install, restart, and add **RHI Planning** in Settings → Devices & services.
3. Open the dashboard editor → Add card → RHI Planning. The card is loaded automatically using the native HA frontend module API; refresh the browser after installation. No manual resource or YAML required. The integration option can disable UX for headless use; explicitly disabled existing entries stay disabled.

Supported TEST: HA OS/Container 2026.11.1, 64-bit amd64 or arm64 (CPython 3.14 musl). No mandatory Foundation. Install the compatible Scheduler component and Scheduler Card resource for native authoring. Specialized owner-provider planners and full mixed-site migration remain unqualified. Keep existing Basic configuration.

## License

See bundled notices for protected TEST permission and third-party licenses.
