# RHI Planning

Unified native Scheduler overview, guarded enable/pause, approved device selection and optional integrated Planning card.

## Installation

1. Add `https://github.com/npinguin/rhi-planning-hacs` as a custom Integration repository in HACS. Enable prereleases and select the published TEST version.
2. Back up Home Assistant, install, restart, and add **RHI Planning** in Settings → Devices & services.
3. Open the dashboard editor → Add card → RHI Planning. The card is loaded automatically using the native HA frontend module API; refresh the browser after installation. No manual resource or YAML required. The integration option can disable UX for headless use; explicitly disabled existing entries stay disabled.

Supported TEST: HA OS/Container 2026.11.1, 64-bit amd64 or arm64 (CPython 3.14 musl). No mandatory Foundation or Scheduler dependency for an otherwise empty Planning installation. **Existing native schedules require the upstream Scheduler integration; household create/edit/delete also requires the separately installed Scheduler Card resource.** RHI Planning does not install or replace that upstream card. Administrators can open native household management in Planning Settings and, for explicit qualified owner/asset contexts, reuse the same native card with exact approved target filters. **The native card's device filter is presentation only, not an authorization boundary:** verify the whole schedule before editing; RHI does not grant native Scheduler permissions. The released Scheduler Component 3.3.9 / Scheduler Card 4.0.20 pair has a known rename defect: a renamed live schedule can disappear until Home Assistant restarts. **Do not rename schedules in this TEST.** The isolated test evidence for other native actions does not establish field acceptance. Approved-target settings and guarded enable/pause remain available. Specialized real-provider parity, strict upstream editor scope guarantees and full mixed-site migration remain unqualified. Keep existing Basic configuration.

## License

See bundled notices for protected TEST permission and third-party licenses.
