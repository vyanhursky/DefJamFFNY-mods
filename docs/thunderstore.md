# Publishing a pack on Thunderstore

Community page: <https://thunderstore.io/c/def-jam-fight-for-ny-recompiled/>.
Project uploads belong to the Thunderstore team **DefJamRecompiled**.

Thunderstore hosts the download; this catalogue still decides what the launcher
offers, pins the exact bytes and sets compatibility and load order. The launcher
installs a Thunderstore ZIP only from a catalogue version that requires
`thunderstore-zip-v1` (see [CONTRACT.md](../CONTRACT.md)), which needs a game
release whose mod helper supports it. Older launchers keep using earlier versions.

## Steps

1. **Build the upload** from the reviewed pack ZIP (or pack folder):

   ```sh
   python tools/thunderstore.py pack --mod menu-ui-hd-wide --version 1.7.1 \
       --source menu-ui-hd-wide-v1.7.0.zip --icon icon-source.png \
       --changelog CHANGELOG.md --mirror https://<r2-origin>/menu-ui-hd-wide/1.7.1/<sha256>/menu-ui-hd-wide-v1.7.1.zip \
       --append
   ```

   It writes `dist/DefJamRecompiled-<Name>-<version>.zip`, checks it with the same
   verifier as the publish workflow, and with `--append` adds the version to
   `mods/<id>.json`. Compatibility (`min_recomp`, capabilities, `depends`,
   `conflicts`, `load_after`) is copied from the newest stable version, or from
   `--from-version`. The README is generated from the catalogue record unless you
   pass `--readme`; the listing summary is the first 250 characters of the
   description unless you pass `--description`. The icon source must be square.
   The same inputs always produce the same bytes.

2. **Version numbers.** Thunderstore accepts `MAJOR.MINOR.PATCH` only, and catalogue
   versions are immutable, so an already published version moves to Thunderstore as
   a new patch version (1.7.0 becomes 1.7.1, same pack). Players who have 1.7.0 are
   then offered that update. Testing versions (`-rc.N`) stay on the existing host.

3. **Upload** the ZIP at <https://thunderstore.io/package/create/> as team
   DefJamRecompiled, community *Def Jam: Fight for NY Recompiled*. Choose the
   category; packs containing AI-generated or AI-restored artwork must also get
   **AI Generated** (Thunderstore global rules).

4. **Check the bytes.** Download the package back from
   `https://thunderstore.io/package/download/DefJamRecompiled/<Name>/<version>/` and
   compare its SHA-256 with the one `pack` printed. If it differs, do not publish:
   the catalogue would refuse every install.

5. **Mirror.** Upload the same ZIP to the `--mirror` URL. The launcher tries the URLs
   in order, so the mirror covers a Thunderstore outage or removal.

6. **Open the catalogue PR** with the appended version, then publish through the
   protected workflow as usual. It downloads every URL and verifies each one.

Thunderstore versions cannot be edited after upload, except the README and
CHANGELOG. To withdraw a version, add it to `revoked_versions` here and deprecate
it on Thunderstore; the download link keeps working for anyone who has it.
