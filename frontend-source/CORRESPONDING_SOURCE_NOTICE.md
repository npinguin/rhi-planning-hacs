# RHI Planning frontend corresponding source

Approval: GRANTED
License: GPL-3.0-only

Owner approval 2026-11-15: the domain-owned presentation source and combined
frontend are licensed GPL-3.0-only. This grant is limited to the frontend and
its corresponding source. The independently loaded backend/business logic
and Home Assistant adapters remain outside that frontend source grant.
Third-party rights remain unchanged.

## Build inputs
- `planning-card.js`: domain presentation source.
- `build.mjs`: deterministic assembly into the integration's frontend.
- `vendor/rhi-ux-core.js` and `vendor/rhi-ux-core.css`: exact pinned Core artifacts.
- `CORE_LOCK.json`: version, source revision and hashes.

The original Core preferred source, license, build script, CSS, JavaScript and
branding asset are publicly accessible at the exact revision:
https://github.com/npinguin/rhi-ux-core/tree/e095ddee728766fda31ae8aac8a7c42e9d63b1c3

Run Core's build script there with Node.js >=20 to recreate the pinned inputs.
The complete license text is in the integration frontend folder. To reproduce
the final card from the public HACS checkout, run
`node frontend-source/build.mjs` at the repository root. This rebuilds only
the frontend; no backend source or compiler is needed.
