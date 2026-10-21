# Def Jam Recompiled mod catalogue

Source-only foundation for the curated mod list used by
[Def Jam Recompiled](https://github.com/vyanhursky/DefJamFFNY-recomp).

**Development: no downloadable mods or trusted catalogue have been published yet.**
The launcher integration and download helper are under development. Local texture
packs remain independent of this catalogue.

This repository holds reviewed JSON metadata, validation tools, and the future
signed GitHub Pages index. Derived artwork downloads belong on an external host
(initially Cloudflare R2), never in this repository. Faithful HD is generated
locally from the player's own dump. The HD/Widescreen Menus pack is a separate mod.

## Development

Python 3.10+; the builder and tests use only the standard library.

```sh
python -m unittest discover -s tests -v
python tools/catalogue.py validate
python tools/catalogue.py build --revision 1 --issued 2026-10-21T00:00:00Z --expires 2026-11-20T00:00:00Z --out /tmp/mod-index.json
```

`build` produces an **unsigned development preview**, never a trusted release.
The catalogue is intentionally empty until the installer, signing and release
acceptance gates pass. No artwork, private key, game binary or dump is included.

See [the contract](CONTRACT.md) and [contribution rules](CONTRIBUTING.md).

## Publishing boundary

PR validation has read-only permissions and no credentials. A future publishing
workflow will rebuild the reviewed main commit, require owner approval through the
`catalogue-release` protected environment, sign the exact index bytes, then deploy
the index and detached signature to GitHub Pages. The helper will pin the public
key, reject rollback/expired installation metadata, and verify package size/hash.
Signing-key provisioning and trusted deployment are not implemented by this
foundation. Do not publish the unsigned preview as a release.

Catalogue/tool source is MIT. Mod artwork has its own credits and permissions;
this repository's licence does not grant rights to game artwork.
