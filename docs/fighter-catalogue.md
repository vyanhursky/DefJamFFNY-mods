# Fighter catalogue verification

The game already supports `fighters-v1` catalogue downloads and shows them under
**Mods → Fighters**. This change adds publishing-side verification and the first
reviewed fighter record; it does not change the signed catalogue schema, game
runtime, trust keys or installed save data.

## Source-bound validation

`tools/fighter_check.py` invokes `fighter_packages.receipt()` from the published
Def Jam Recompiled **v1.2.1** source at
`2496bd3429a854a842701070cbeb5a54c5e3f445`. The source is game-free and needs no
dump, submodule build, lifted code or game executable for inventory checks.
Verification CI checks out that immutable commit into `.fighter-validator/`.
For local development, clone the tag there as shown in README, or set
`DEFJAM_FIGHTER_VALIDATOR_SOURCE` to a clean checkout at that exact commit.

The bridge refuses missing/different/modified source and extra Python files in
its setup directory. Its child uses isolated Python (`-I -B`) and imports only
from the verifier-configured source; the downloaded pack is never an import
path or command source. Source/configuration pin changes require review.

The released validator checks closed resource source schemas, descriptors,
SHA-256 hashes, declared inventory and file/byte limits. The catalogue additionally
checks PNG and mono PCM16 WAV containers, and binds pack identity/version to the
archive/catalogue record. Native data extensions are admitted only for a fighter
manifest, and undeclared files remain refused. No host executables or scripts
are admitted. Runtime compilation still validates game-specific choices, rig/
palette/event joins and owned native resources against the player's dump.

The existing key-free verification job runs these checks and malware scanning.
The protected signing job has no fighter-source checkout, does not call the
bridge, and signs only metadata matching reviewed main and verified history.
The private signing key is not made available to package parsing or source imports.

## 2PAC 1.6.36

The Thunderstore download is pinned to the owner-uploaded bytes: 106,100,388
archive bytes, SHA-256
`cc21219670b0f8b58a1c28d5f3d310a7827d95590535197ce4d682a3aa725fde`.
Its `fighter-2pac-ffny-recomp/` payload is 117 files / 107,137,857 unpacked bytes.
Thunderstore metadata, the approved README and the chosen 256px icon are outside
that folder and not installed into the game's mod directory.

This is one selectable fighter with Shirtless, Red Wings and Birdie outfits.
The compatible minimum is game **1.2.1** for the reviewed victory/finger compiler
contracts. Existing 1.2.0 support alone does not qualify the full performance.
Credits are whoonthetrack (original textures/initial modpack) and vyanhursky
(UI/animation); catalogue metadata does not grant a new asset redistribution licence.

Native evidence is inherited from the approved macOS/default CAF outfit at
Terrordome through entrance, combat, victory and results. Catalogue ZIP/hash/
inventory validation is not a new game run, a Steam Deck qualification, or
exhaustive acceptance of all outfits, venues, variants, skip/rematch and modes.
The reported Deck startup delay remains under game issue #292 investigation.

## Publication

After review/merge, run **Publish signed catalogue** on main without bootstrap.
It verifies existing signed history and downloads, then awaits the protected
`catalogue-release` environment before signing and Pages deployment. Verify the
live signature/new revision before claiming the fighter is available in-game.
Users then refresh **Mods → Fighters**, select the pack and **Install and enable**.
Keep the pack ID stable for subsequent catalogue updates.
