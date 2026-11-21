# Contributing

The catalogue is in development; please discuss a submission before adding it.

- One mod per pull request, one `mods/<stable-id>.json` file.
- Describe credits, permissions, compatibility, actual changes and download size.
- All downloadable versions must be immutable, pinned by byte size and SHA-256.
- Never commit game data, derived artwork, archives, executables, captures or keys.
- Derived assets use third-party download URLs; metadata does not license them.
- Faithful HD remains a local-generation option, not a redistributed download.
- Texture, language and typed fighter packages are supported; no executable hooks.
- Fighter submissions must use the pinned released data-only inventory validator
  described in `docs/fighter-catalogue.md`; adding filename extensions alone is insufficient.
- Existing published versions stay byte-identical; withdraw with revocation.
- Review source, workflow changes, downloaded content and scan results before release.

PR checks only validate this draft metadata. Passing them does not constitute
content approval, a malware scan, or authorization to publish a trusted index.
