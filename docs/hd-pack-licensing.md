# HD pack permissions and attribution

From **HD Menus and UI 1.7.1**, **HD Fighters 1.0.1** and
**HD Fighter Portraits 1.0.1**, original, legally protectable contributions by
**Vlad Yanhursky / vyanhursky** are licensed under
[Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/).

This applies only to rights held by that contributor in original texture-mapping
selection/arrangement, creative restoration and upscale edits, widescreen
extensions and pack selection/assembly. It does not assert copyright over factual
texture IDs, mechanical mappings, automated upscaling or AI-generated pixels.

## Sharing and reuse

The licence grants permission in advance to share and adapt covered contributions
for noncommercial purposes. Individual approval is not required for uses allowed
by the licence. Give appropriate credit, retain the licence notice and link,
and identify changes. Credit may be provided in any reasonable manner, without
suggesting endorsement. Suggested credit:

> Texture mapping, restoration and upscale work by Vlad Yanhursky / vyanhursky.

Link to [this project](https://github.com/vyanhursky/DefJamFFNY-mods) and
[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). The licence
is irrevocable while its terms are met; it does not impose ShareAlike.
Commercial use of covered contributions requires separate permission from the
relevant rights holder. Read the [complete legal text](../licenses/CC-BY-NC-4.0.txt);
this summary adds no restrictions and the legal text controls.

## Exclusions and separate licences

Original Def Jam: Fight for NY textures, characters, logos and other game artwork
remain subject to their respective rights holders' rights. No ownership of, or
permission concerning, that material is claimed or granted. Licensing the original
contributions does not supply all permissions potentially needed to redistribute
a complete derived game texture. Any other third-party contributions retain
their own terms.

The catalogue and tooling source remain MIT-licensed. **ZARF's Spanish translation
and adaptation remain CC BY-NC-SA 4.0**, with their existing credit requirements;
this release does not modify that mod or its catalogue record.

## Release records and reproduction

Each new ZIP contains the scoped [LICENSE.txt notice](../licenses/HD-PACKS-NOTICE.txt)
and the unmodified [CC BY-NC 4.0 legal text](../licenses/CC-BY-NC-4.0.txt).
README and release receipts identify the new version, attribution and source
release. Prior archives and version descriptors are not overwritten. Older
archives retain their bundled notices; these releases make the new permission
and scope explicit.

`tools/relicense_hd_packs.py` verifies the original published archive SHA-256,
changes only release documentation and the manifest display name, and checks
that all other manifest settings and texture/widescreen mappings are unchanged.
It produces deterministic ZIPs, per-file hashes and archive descriptors using
a streaming sink. Source artworks are not included in this repository.

Before publication, compare every image hash with the preceding release, validate
new ZIP entries/CRC and images, check public SHA-256/length/range support, and pass
the normal protected download/archive/malware verification and signed deployment.
These packaging checks do not expand the previous releases' native playtest claims.
