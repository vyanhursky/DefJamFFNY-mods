# Def Jam Recompiled mod catalogue

Source for the signed curated mod list used by
[Def Jam Recompiled](https://github.com/vyanhursky/DefJamFFNY-recomp).

Open Mods in the launcher and refresh the catalogue. **HD Widescreen Menus 1.4.0**
is available on game 0.12.1 or later. Update the mod and restart the game; no
reinstall is required. See [menu pack releases](docs/menu-ui-hd-wide.md) for scope,
compatibility and immutable download records. Local texture packs remain supported.

This repository holds reviewed JSON metadata, validation tools, and the
signed GitHub Pages index. Derived artwork downloads belong on an external host
(initially Cloudflare R2), never in this repository. Faithful HD is generated
locally from the player's own dump. The HD/Widescreen Menus pack is a separate mod.

## Development

Python 3.11+; the builder uses only the standard library. Release verification
and its tests additionally use pinned `cryptography==50.0.2`, `cffi==2.0.0`,
`pycparser==2.23` and `Pillow==12.3.0`, as recorded in the workflows.

```sh
python -m unittest discover -s tests -v
python tools/catalogue.py validate
python tools/catalogue.py build --revision 1 --issued 2026-10-21T00:00:00Z --expires 2026-11-20T00:00:00Z --out /tmp/mod-index.json
```

`build` produces an **unsigned development preview**, never a trusted release.
Published catalogue history and version records are immutable. A stable-channel
release may reuse an accepted candidate archive without changing its bytes.
No artwork, private key, game binary or dump is included.

See [the contract](CONTRACT.md) and [contribution rules](CONTRIBUTING.md).

## Publishing boundary

PR validation has read-only permissions and no credentials. The publishing
workflow rebuilds the reviewed main commit, requires owner approval through the
`catalogue-release` protected environment, signs the exact index bytes, then deploys
the index and detached signature to GitHub Pages. The helper will pin the public
key, reject rollback/expired installation metadata, and verify package size/hash.
The signing public key is pinned in `catalogue-keys.json`; its private counterpart
is held in the protected environment, never in source. The owner must approve the
publishing job. The live signed catalogue is published through GitHub Pages.
Do not publish the unsigned preview as a release.

Catalogue/tool source is MIT. Mod artwork has its own credits and permissions;
this repository's licence does not grant rights to game artwork.

Before the first Pages publication, choose the explicit **bootstrap** workflow
option; it accepts the reviewed initial entries only when no signed history
exists. Later publications must fetch and verify existing history. An unexpected HTTP 404 fails closed rather than resetting
revision/history. Package validation runs without signing credentials. The
protected signer installs only exact hash-pinned binary wheels from
`requirements-signing.txt` on CPython 3.13, checks the prepared metadata against
reviewed source, and never parses downloaded mod images.
