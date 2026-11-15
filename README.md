# RHI Planning

Unified native Scheduler overview, guarded enable/pause, approved device selection and optional integrated Planning card using the existing Scheduler Card.

## Installation

1. Add `https://github.com/npinguin/rhi-planning-hacs` as a custom Integration repository in HACS. Enable prereleases and select the published TEST version.
2. Back up Home Assistant, install, restart, and add **RHI Planning** in Settings → Devices & services.
3. Enable optional UX in integration options. Add `/rhi_planning/frontend/planning-card.js` as a JavaScript module dashboard resource and add a card with `type: custom:rhi-planning-overview-card` to an existing view.

Supported TEST: HA OS/Container 2026.11.1, 64-bit amd64 or arm64 (CPython 3.14 musl). No mandatory Foundation. Install the compatible Scheduler component and Scheduler Card resource for native authoring. Specialized owner-provider planners and full mixed-site migration remain unqualified. Keep existing Basic configuration.

## License

See bundled notices for protected TEST permission and third-party licenses.
