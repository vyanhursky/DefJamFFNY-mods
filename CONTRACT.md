# Draft texture catalogue contract, schema 1

One `mods/<id>.json` source file per mod. `tools/catalogue.py` strictly validates
the fields below; unknown fields fail. This draft is not a deployed protocol.

Mod fields: `id`, `name`, `description`, `authors` (nonempty string list),
`class` (`linked` or `original`), `licence` (text describing actual permissions),
`homepage` (HTTPS), `versions` (nonempty list), `revoked_versions` (version strings).
Identity is a stable lowercase hyphenated slug, distinct from an export folder.

Version fields: `version` (three-part SemVer, optional prerelease), `channel`
(`stable` or `prerelease`), `min_recomp` (three-part version), `capabilities`
(required runtime capability names), `reviewed` (ISO date), `depends`, `conflicts`,
`load_after` (lists of stable mod IDs), and `archive`.
`load_after` is a recommendation, not a hidden second load order. The initial
helper will support texture packs only; no scripts, recipes, or native code.

Archive fields: `urls` (nonempty HTTPS list), `size` (compressed bytes),
`unpacked_size` (payload bytes), `file_count`, `sha256` (lowercase hex),
`root` (the single pack folder inside the ZIP). Counts/sizes must be positive.
Runtime minimum/capability values must come from measured compatibility evidence.
An entry is not compatible merely because its JSON validates.

Released versions are immutable. Append versions; use `revoked_versions` to
withdraw existing versions without changing their pinned records. Version order
is publication order, not version comparison. Clients select compatible versions
using SemVer and channel rules. Source builds sort mods by ID and JSON keys; the
same sources and explicit header inputs produce identical bytes.

Output header: `schema=1`, `game=defjam-ffny-recomp`, positive `revision`, UTC
`issued` and `expires` timestamps, and `mods`. Revision must increase for each
trusted release; expiry is later than issue. The future signature covers exact
output bytes. A signed timestamp alone does not prevent replay; clients retain
the highest accepted revision and require nonexpired metadata for new installs.

The foundation validates metadata only. Before any trusted release, add isolated
archive download/hash/layout checks, append-only comparison against the published
catalogue, signing, key pinning/rotation, and protected deployment. No SHA-256
placeholder or untested package should appear in a live catalogue.
