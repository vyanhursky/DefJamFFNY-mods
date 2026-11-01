# HD Widescreen Menus releases

This catalogue owns published version metadata, compatibility, download pins, credits and concise release notes. The version descriptors in [mods/menu-ui-hd-wide.json](../mods/menu-ui-hd-wide.json) are authoritative; historical package records remain immutable.

| Version | Download bytes | Unpacked bytes | Files |
|---|---:|---:|---:|
| [1.0.0-rc2](https://pub-9167b11f83f24f2a9e21af7f0e225057.r2.dev/menu-ui-hd-wide/1.0.0-rc2/43bbb22cd14197091143623551f350a0b7ff622f0efccb1da058f491e7157634/menu-ui-hd-wide-v1-rc2.zip) | 421,563,157 | 423,392,524 | 326 |
| [1.0.0](https://pub-9167b11f83f24f2a9e21af7f0e225057.r2.dev/menu-ui-hd-wide/1.0.0-rc2/43bbb22cd14197091143623551f350a0b7ff622f0efccb1da058f491e7157634/menu-ui-hd-wide-v1-rc2.zip) | 421,563,157 | 423,392,524 | 326 |
| [1.1.0](https://pub-9167b11f83f24f2a9e21af7f0e225057.r2.dev/menu-ui-hd-wide/1.1.0/95200fe8a01402a1b50695135102e6349309342c22132d0300aa62a92c79e724/menu-ui-hd-wide-v1.1.0.zip) | 536,557,056 | 538,706,855 | 404 |
| [1.2.0](https://pub-9167b11f83f24f2a9e21af7f0e225057.r2.dev/menu-ui-hd-wide/1.2.0/bb9109ef1fa77f78796afd051c4d6c602f5dbfa0554e698f3b8746be4cbd3589/menu-ui-hd-wide-v1.2.0.zip) | 643,020,896 | 646,222,232 | 1,528 |
| [1.3.0](https://pub-9167b11f83f24f2a9e21af7f0e225057.r2.dev/menu-ui-hd-wide/1.3.0/82ad6d53f3161b612110cdd84e3f9d0bde2f517a9a9f6410f9e52afcf963de24/menu-ui-hd-wide-v1.3.0.zip) | 679,627,331 | 683,803,577 | 1,706 |
| [1.4.0](https://pub-9167b11f83f24f2a9e21af7f0e225057.r2.dev/menu-ui-hd-wide/1.4.0/f3d79f86a024b5786919ef2d6f38b1f599cb49a151d031b4a85023a5f480848d/menu-ui-hd-wide-v1.4.0.zip) | 601,895,156 | 605,772,797 | 1,746 |

## 1.4.0 — combined approved restoration

Combines 1,343 approved reconstructed menu/UI mappings, including 953 additions since 1.3, while retaining previous widescreen backgrounds and repaired joins. Five accepted sources retain baseline artwork. Contains 1,522 native mappings, 80 widescreen registrations and 1,744 PNGs. Faithful HD is optional and separate.

All packaged PNGs passed lossless RGBA/metadata equality checks. Optimization saved 111,659,732 PNG bytes (15.61%); the combined ZIP is 77,732,175 bytes smaller than 1.3.

Minimum game is **0.12.1**, capabilities `textures-v1` and `wide-v1`. Refresh the launcher catalogue, update the mod and restart the game; no reinstall required. The unchanged released helper completed a real signed-network 1.3→1.4 update and rollback in a disposable root with exact installed/backup hashes and an unchanged isolated save marker. Six native routes supplied representative acceptance; not every language or variant was visited.

[Catalogue PR9](https://github.com/vyanhursky/DefJamFFNY-mods/pull/9) and the [protected publication workflow](https://github.com/vyanhursky/DefJamFFNY-mods/actions/runs/41217382346) published 1.4.0 in signed revision 9 with preserved history and the unchanged signing key. That is its publication revision, not a claim about the current live revision. No metadata/index regeneration is required for this documentation.

## Earlier versions

1.3.0 introduced the first 390 accepted reconstructed mappings. 1.2.0 applied the earlier Stronger edge clarity pass to 1,140 text overrides, including 214 banner variants. 1.1.0 added the approved missing User ID/Teams/Venue backgrounds and repaired wide joins. The initial stable 1.0.0 reused the accepted RC2 archive. All earlier descriptors and bytes remain available unchanged.

## Authoring and runtime evidence

Reusable [menu procedures](https://github.com/vyanhursky/DefJam-Modding-Tools/blob/main/docs/menu-text-restoration.md), exporters, native registration and compression belong in Modding Tools. Actual generations, prompts, per-texture approvals, detailed batch ledgers and local checkpoint paths remain in the private authoring workspace. This source repository does not bundle those records or artwork. Runtime loader/installer/native diagnostic investigations belong in DefJamFFNY-recomp. The separate fire-escape geometry repair is game code and is not delivered by this texture ZIP.
