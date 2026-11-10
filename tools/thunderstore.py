#!/usr/bin/env python3
"""Build a Thunderstore upload from a reviewed pack and its catalogue record.

The upload is the pack folder unchanged plus manifest.json, README.md, icon.png
and optionally CHANGELOG.md at the ZIP root. The game helper installs it when the
catalogue version requires `thunderstore-zip-v1` (CONTRACT.md). The output is
deterministic: the same inputs give the same bytes, so the SHA-256 printed here
is the one Thunderstore must serve back.

    python tools/thunderstore.py pack --mod menu-ui-hd-wide --version 1.7.1 \\
        --source menu-ui-hd-wide-v1.7.0.zip --icon icon-source.png --append

`--append` adds the new version to mods/<id>.json, copying compatibility from
the newest stable version (or `--from-version`). Upload the ZIP, download it back
from Thunderstore and compare its SHA-256 before publishing the catalogue.
"""
import argparse
import datetime as dt
import io
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import tempfile
import zipfile

import catalogue
import package_check

ROOT = Path(__file__).resolve().parents[1]
TEAM = 'DefJamRecompiled'
GAME = 'https://github.com/vyanhursky/DefJamFFNY-recomp'
STAMP = (1980, 1, 1, 0, 0, 0)
STORED = {'.png'}  # already compressed; everything else is deflated


def package_name(text):
    """Thunderstore names allow letters, digits and underscores; underscores show as spaces."""
    name = re.sub(r'[^A-Za-z0-9]+', '_', text.replace("'", '')).strip('_')
    catalogue.require(name and len(name) <= 128, 'Cannot derive a Thunderstore name; pass --name')
    return name


def short_description(text, limit=250):
    text = ' '.join(text.split())
    if len(text) <= limit:
        return text
    cut = text[:limit]
    end = max(cut.rfind('. '), cut.rfind('.)'))
    if end >= limit // 3:
        return cut[:end + 1]
    return cut[:cut.rfind(' ', 0, limit - 1)].rstrip(',;:') + '…'


def make_icon(source):
    from PIL import Image
    with Image.open(source) as picture:
        catalogue.require(picture.width == picture.height, 'Icon source must be square')
        icon = picture.convert('RGBA').resize((256, 256), Image.Resampling.LANCZOS)
    out = io.BytesIO()
    icon.save(out, format='PNG', optimize=True)
    return out.getvalue()


def readme(mod, version, root):
    authors = ', '.join(mod['authors'])
    return f"""# {mod['name']}

{mod['description']}

## Install

For [Def Jam Recompiled]({GAME}) {version['min_recomp']} or later.

**Recommended:** open **Mods** in the game's launcher, refresh the catalogue and install
**{mod['name']}** there. The launcher verifies the download, offers updates and lets you set
its priority in Load Order.

**By hand:** extract the `{root}` folder from this download into the `mods` folder of your
Def Jam Recompiled data folder, then enable it on the launcher's Mods page. A copy installed
by hand is a local mod: the launcher does not update it.

## Credits and licence

By {authors}.

{mod['licence']}

More information: {mod['homepage']}
"""


def payload(source):
    """(root, [(relative path, opener)]) from a pack ZIP with one root folder, or a pack folder."""
    source = Path(source)
    if source.is_dir():
        catalogue.slug(source.name)
        rows = []
        for path in sorted(p for p in source.rglob('*') if p.is_file()):
            relative = path.relative_to(source).as_posix()
            catalogue.require(not path.is_symlink(), 'Linked file in pack folder: ' + relative)
            rows.append((relative, lambda path=path: path.open('rb')))
        return source.name, rows
    bundle = zipfile.ZipFile(source)
    rows, roots = [], set()
    for info in bundle.infolist():
        parts = PurePosixPath(info.filename.rstrip('/')).parts
        roots.add(parts[0])
        if not info.is_dir():
            catalogue.require(len(parts) > 1, 'Source ZIP has a file outside its pack folder: ' + info.filename)
            rows.append(('/'.join(parts[1:]), lambda info=info: bundle.open(info)))
    catalogue.require(len(roots) == 1, 'Source ZIP needs exactly one pack folder at its root')
    root = roots.pop()
    catalogue.slug(root)
    return root, sorted(rows)


def entry(name, compress=True):
    info = zipfile.ZipInfo(name, STAMP)
    info.external_attr = 0o644 << 16
    info.compress_type = (zipfile.ZIP_STORED if not compress or PurePosixPath(name).suffix.lower() in STORED
                          else zipfile.ZIP_DEFLATED)
    return info


def build_zip(out, wrapper, root, rows):
    with zipfile.ZipFile(out, 'w') as bundle:
        for name in sorted(wrapper):
            bundle.writestr(entry(name), wrapper[name])
        for relative, opener in rows:
            with opener() as source, bundle.open(entry(root + '/' + relative), 'w') as target:
                shutil.copyfileobj(source, target, 1024 * 1024)


def base_version(mod, requested=None):
    rows = [v for v in mod['versions'] if v['version'] not in mod['revoked_versions']]
    if requested:
        rows = [v for v in rows if v['version'] == requested]
        catalogue.require(rows, 'Unknown --from-version')
    else:
        rows = [v for v in rows if v['channel'] == 'stable'] or rows
    return rows[-1]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=('pack',))
    parser.add_argument('--mod', required=True, help='Catalogue ID (mods/<id>.json)')
    parser.add_argument('--version', required=True, help='New version; Thunderstore takes MAJOR.MINOR.PATCH only')
    parser.add_argument('--source', type=Path, required=True, help='Reviewed pack ZIP (one root folder) or pack folder')
    parser.add_argument('--icon', type=Path, required=True, help='Square image; resized to 256x256 PNG')
    parser.add_argument('--from-version', help='Copy compatibility from this version (default: newest stable)')
    parser.add_argument('--name', help='Thunderstore package name (default: from the mod name)')
    parser.add_argument('--description', help='Listing summary, 250 characters at most (default: from the catalogue)')
    parser.add_argument('--readme', type=Path, help='README.md to use instead of the generated one')
    parser.add_argument('--changelog', type=Path, help='Optional CHANGELOG.md')
    parser.add_argument('--team', default=TEAM)
    parser.add_argument('--mirror', action='append', default=[], help='Extra HTTPS URL serving the same ZIP bytes')
    parser.add_argument('--mods', type=Path, default=ROOT / 'mods')
    parser.add_argument('--out', type=Path, default=ROOT / 'dist')
    parser.add_argument('--append', action='store_true', help='Add the version to mods/<id>.json')
    args = parser.parse_args(argv)

    catalogue.slug(args.mod)
    path = args.mods / (args.mod + '.json')
    mod = catalogue.validate_mod(json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=catalogue.unique_object))
    catalogue.require(re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', args.version),
                      'Thunderstore versions are MAJOR.MINOR.PATCH without a suffix')
    catalogue.require(all(v['version'] != args.version for v in mod['versions']),
                      'Version already published; catalogue versions are immutable')
    base = base_version(mod, args.from_version)
    name = args.name or package_name(mod['name'])
    catalogue.require(re.fullmatch(r'[A-Za-z0-9_]{1,128}', name), 'Invalid Thunderstore name')
    description = args.description or short_description(mod['description'])
    catalogue.require(len(description) <= 250, 'Description exceeds 250 characters')

    root, rows = payload(args.source)
    manifest = dict(name=name, version_number=args.version, website_url=mod['homepage'],
                    description=description, dependencies=[])
    wrapper = {
        'manifest.json': (json.dumps(manifest, indent=2, ensure_ascii=False) + '\n').encode('utf-8'),
        'README.md': (args.readme.read_text(encoding='utf-8-sig') if args.readme else readme(mod, base, root)).encode('utf-8'),
        'icon.png': make_icon(args.icon),
    }
    if args.changelog:
        wrapper['CHANGELOG.md'] = args.changelog.read_text(encoding='utf-8-sig').encode('utf-8')

    args.out.mkdir(parents=True, exist_ok=True)
    out = args.out / f'{args.team}-{name}-{args.version}.zip'
    build_zip(out, wrapper, root, rows)
    with zipfile.ZipFile(out) as bundle:
        files = [i for i in bundle.infolist() if not i.is_dir() and i.filename not in wrapper]
    archive = dict(urls=[f'https://thunderstore.io/package/download/{args.team}/{name}/{args.version}/', *args.mirror],
                   size=out.stat().st_size, unpacked_size=sum(i.file_size for i in files), file_count=len(files),
                   sha256=package_check.sha(out), root=root)
    capabilities = list(base['capabilities'])
    if package_check.STOREFRONT not in capabilities:
        capabilities.append(package_check.STOREFRONT)

    # The publish workflow runs this same check on the downloaded bytes.
    with tempfile.TemporaryDirectory(prefix='defjam-thunderstore-') as scratch:
        pack = package_check.unpack_archive(out, archive, Path(scratch) / 'pack', storefront=True, version=args.version)
    catalogue.require(set(pack['capabilities']) <= set(capabilities), 'Pack needs capabilities the base version lacks')

    version = dict(version=args.version, channel='stable', min_recomp=base['min_recomp'], capabilities=capabilities,
                   reviewed=dt.date.today().isoformat(), depends=base['depends'], conflicts=base['conflicts'],
                   load_after=base['load_after'], archive=archive)
    if args.append:
        updated = dict(mod, versions=mod['versions'] + [version])
        catalogue.validate_mod(json.loads(json.dumps(updated), object_pairs_hook=catalogue.unique_object))
        path.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(upload=str(out), package=f'{args.team}-{name}-{args.version}', version=version), indent=2))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        sys.exit('thunderstore.py: ' + str(error))
