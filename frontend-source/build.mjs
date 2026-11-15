// Rebuild package-local Planning frontend from pinned Core and domain source.
import fs from "node:fs";import crypto from "node:crypto";import assert from "node:assert/strict";
const read=p=>fs.readFileSync(new URL(p,import.meta.url),"utf8");
const js=read("./vendor/rhi-ux-core.js"),css=read("./vendor/rhi-ux-core.css"),domain=read("./planning-card.js"),lock=JSON.parse(read("./CORE_LOCK.json"));
const hash=x=>crypto.createHash("sha256").update(x).digest("hex");assert.equal(hash(js),lock.js_sha256);assert.equal(hash(css),lock.css_sha256);
fs.writeFileSync(new URL("../custom_components/rhi_planning/frontend/planning-card.js",import.meta.url),js+"\nconst RHI_BUNDLED_CORE_CSS="+JSON.stringify(css)+";\n"+domain);
