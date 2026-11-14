# HD Fighters

Independent 3D fighter texture mod, catalogue ID `hd-fighters`.

## 1.1.0 — final fighter restorations

Adds the last **13 owner-approved restorations** using Google Gemini / Nano Banana Pro:
Carmen Electra B and David Banner main atlases, plus 11 injury maps for David Banner,
Xzibit, Sticky Fingaz A/B, Blaze Story C, D-Mob C and Memphis Bleek. Banner's crown
hair tile is corrected in his main and both injury maps; his original costume
artwork is retained. The other **205 PNG files are byte-identical to 1.0.2**.

The pack retains **218 texture IDs** for **69 named characters**: 80 main/outfit/Story
atlases, 133 secondary maps (132 injury images and one uninjured head), and five
shared inputs. All **213 fighter atlas/secondary entries** now have AI-assisted
Rich Original Detail restorations. The five shared sparkle/tape inputs remain
native originals for shader/blend fidelity. No local-neural trials are included.

| Texture group | Original | HD Fighters 1.1 |
| --- | --- | --- |
| Main/outfit/Story atlases | 512 × 512 | 2048 × 2048 |
| Secondary/injury maps | 256 × 256 | 1024 × 1024 |
| Four shared sparkle inputs | 64 × 64 | 64 × 64, unchanged |
| Shared tape input | 32 × 64 | 32 × 64, unchanged |

[Download 1.1.0](https://pub-9167b11f83f24f2a9e21af7f0e225057.r2.dev/hd-fighters/1.1.0/eddb7f68011788751472739de059aae9eaf130b8b479fcdcc14c72d88df0be0e/hd-fighters-v1.1.0.zip): **681,534,159 bytes**
(681.53 MB); unpacked **681,681,076 bytes**, **223 files**.
SHA-256: `eddb7f68011788751472739de059aae9eaf130b8b479fcdcc14c72d88df0be0e`.

Install/update **HD Fighters** through **Mods > Textures > Browse > Refresh Catalogue**,
enable it, give it priority over optional Faithful HD/Recomp HD fighter textures,
then restart. Faithful HD is optional; no rebuild is needed. Manual installs use
the intact `hd-fighters-v1-1-0` folder inside the game's data `mods` directory.
This launcher archive retains game **0.12.1** / **textures-v1** compatibility.
Thunderstore receives a separate wrapper around the identical 223-file pack payload.

Source UV geometry, material alpha and muted skin/clothing palette are retained.
No models, rigs, animations, executable code or gameplay changes are included.
Artwork approval is complete; representative native injury/Story transitions,
transparent materials and distant mip behavior still need playtesting.

Original contributions retain **CC BY-NC 4.0**, with both licence files byte-identical
to the prior release. Original game artwork and third-party rights are excluded.
[Interactive comparisons](https://vyanhursky.github.io/DefJamFFNY-recomp/hd-fighters/)
and the existing approved screenshots remain available.

## 1.0.1 — licence and attribution update

The original, legally protectable contributions by **Vlad Yanhursky / vyanhursky**
are now offered under **CC BY-NC 4.0**. See [the shared HD pack permissions](hd-pack-licensing.md)
for scope, required credit and third-party exclusions. The ZIP includes `LICENSE.txt`
and the complete `CC-BY-NC-4.0.txt` legal text. This is a licence-only update from
1.0.0: all 218 texture files, 218 native
mappings and 0 widescreen registrations are unchanged. Only the display
name, release receipt and documentation change. Runtime minimum, capabilities,
load-order recommendations and existing validation limitations remain unchanged.

[Download 1.0.1](https://pub-9167b11f83f24f2a9e21af7f0e225057.r2.dev/hd-fighters/1.0.1/cc6d43e4008d99c1dcaac207bc47d89e562f4cb9aa0e7b7993a423fb885b43a8/hd-fighters-v1.0.1.zip): **669,268,839 bytes**
(669.3 MB); unpacked **669,225,548 bytes**, **223 files**.
SHA-256: `cc6d43e4008d99c1dcaac207bc47d89e562f4cb9aa0e7b7993a423fb885b43a8`.

Existing archives and published version descriptors remain immutable. This licence
notice accompanies this new release; it does not silently rewrite older ZIPs or
change the licensing of source code, original game artwork or ZARF's translation.

## Artwork scope and validation

Retains the 1.0.0 release's 218 fixed-roster texture mappings: main outfits,
in-engine Story states, injury maps and five shared inputs. Includes 200 Rich
Original Detail restorations with source-palette matching and preserved material
alpha, plus explicit original/Lanczos fallbacks. Local-neural trials are excluded.
Created-player customization, 2D portraits, menus and prerecorded video are separate.
Faithful HD is optional. Game **0.12.1** or later and `textures-v1` are required.

Enable HD Fighters in Mods, put it higher than optional Faithful HD in the launcher
load order, and restart the game. No game rebuild is needed. Artwork and mapping
equivalence for this documentation-only release do not resolve outstanding native
playtest coverage: injury/Story switching, transparent materials and distant mip
behavior still need representative in-game checks. Existing acceptance limitations
are preserved; no new native playtest is claimed for this licence update.

Exact version descriptors, previous release URLs and compatibility are in
[the catalogue record](../mods/hd-fighters.json).
