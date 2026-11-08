# HD Fighter Portraits 1.0.0

Independent 2D portrait mod, catalogue ID `hd-fighter-portraits`. Contains 2,184
native textures: the 1,334 approved Select/Story/team/roster/result textures from
combined Menus 1.5, with their published PNG bytes unchanged, plus 850 new loading
textures covering all 294 approved two-, three- and four-player portrait layouts.
Alternate/injury poses and the final Bubba 3p and Carmen 4p corrections are included.
The original per-layout UV geometry controls native fragments; no independent
axis scaling is used. Source alpha and unedited native atlas exteriors are exact.

Menu scenery, headings, name banners, UI icons and loading backgrounds belong to
[HD Menus and UI](menu-ui-hd-wide.md). The 3D **HD Fighters** mod is separate.
Either split pack works independently; the current pair has no overlapping IDs.
Faithful HD is optional. Requires game **0.12.1**, capability `textures-v1`; no
game rebuild/reinstall is needed. Enable the packs you want and restart.

## Migration from combined Menus 1.5

Install HD Fighter Portraits and update Menus to 1.6 to keep all previous artwork
and add loading portraits. Updating Menus alone removes its portrait component.
The manager does not silently add dependencies. Older 1.5 bytes stay available.
If temporarily using combined Menus 1.5 with Portraits, load Portraits afterward;
the 1,334 shared Select/Story mappings contain identical published PNG bytes.

## Immutable archive

Download: 751,193,605 bytes (751.2 MB); unpacked:
752,327,397 bytes; 2,187 files. Exact
URL, SHA-256, root and compatibility are pinned in
[the catalogue record](../mods/hd-fighter-portraits.json). Lossless PNG optimization
preserves every decoded RGBA byte and every non-IDAT metadata chunk.

The unchanged released 0.12.1 installer accepts the archive. Native validation
results accompany the release PR; representative checks do not certify every
fighter or platform. Production prompts, per-image approvals, raw outputs and
working review projects remain private and preserved for future revisions.

Derived game artwork; rights remain with their respective owners. The catalogue
source MIT licence does not cover artwork. Credits: vyanhursky.
