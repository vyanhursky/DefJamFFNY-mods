#!/usr/bin/env python3
"""Repackage an HD ZIP with scoped CC notices; preserve every texture and mapping.

The source archive and output sink are supplied by the release operator. A sink
need only support write/flush, so large archives can be hashed or uploaded without
creating another local artwork copy. This module performs no network operations.
"""
import configparser
import copy
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NOTICE = ROOT / 'licenses/HD-PACKS-NOTICE.txt'
LEGAL = ROOT / 'licenses/CC-BY-NC-4.0.txt'
CREDIT = 'Vlad Yanhursky / vyanhursky'
LICENSE_URL = 'https://creativecommons.org/licenses/by-nc/4.0/'
LICENSE_SUMMARY = ('CC BY-NC 4.0 for original, legally protectable contributions by '
                   + CREDIT + '; original game artwork and other third-party '
                   'rights are excluded. See the bundled licence notice.')


class HashSink:
    def __init__(self):
        self.digest = hashlib.sha256()
        self.size = 0

    def write(self, data):
        self.digest.update(data)
        self.size += len(data)
        return len(data)

    def flush(self):
        pass


def manifest_sections(data):
    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str
    parser.read_string(data.decode('utf-8-sig'))
    return {section: dict(parser[section]) for section in parser.sections()}


def repackage(source, output, *, mod_id, name, old_version, version, source_sha256):
    """Return a descriptor and verification receipt for exact deterministic bytes."""
    from package_check import safe_relative
    source = Path(source)
    with source.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != source_sha256:
            raise ValueError('Source ZIP does not match its published pin')
    root = mod_id + '-v' + version.replace('.', '-')
    safe_relative(root)
    notice, legal = NOTICE.read_bytes(), LEGAL.read_bytes()
    assert b'Attribution-NonCommercial 4.0 International' in legal
    assert CREDIT.encode() in notice
    sink = HashSink()

    class Tee:
        def write(self, data):
            written = output.write(data)
            if written is not None and written != len(data):
                raise OSError('Short archive write')
            sink.write(data)
            return len(data)

        def flush(self):
            output.flush()

    records, changed, unchanged = {}, [], []
    with zipfile.ZipFile(source) as original:
        entries = [info for info in original.infolist() if not info.is_dir()]
        roots = {info.filename.split('/')[0] for info in entries}
        if len(roots) != 1:
            raise ValueError('Expected a single source pack root')
        old_root = roots.pop()
        names = set()
        for info in entries:
            safe_relative(info.filename)
            if info.filename.casefold() in names or info.flag_bits & 1:
                raise ValueError('Duplicate or encrypted source entry')
            names.add(info.filename.casefold())
        replacements = {}
        manifest = original.read(old_root + '/manifest.ini')
        before = manifest_sections(manifest)
        old_name = before['pack']['name']
        pattern = r'(?m)^(name\s*=\s*)' + re.escape(old_name) + r'\s*$'
        updated, count = re.subn(pattern, lambda m: m[1] + name + ' ' + version,
                                 manifest.decode('utf-8-sig'), count=1)
        if count != 1:
            raise ValueError('Could not locate the pack display name')
        replacements['manifest.ini'] = updated.encode()
        after = manifest_sections(replacements['manifest.ini'])
        expected = copy.deepcopy(before)
        expected['pack']['name'] = name + ' ' + version
        assert after == expected, 'Mapping or runtime policy changed'
        readme = original.read(old_root + '/README.txt').decode('utf-8-sig')
        readme = readme.replace(old_version, version)
        readme = readme.replace('Credits: vyanhursky;', 'Credits: ' + CREDIT + ';')
        readme = readme.replace('This archive is a local release candidate; validation and publication\nstatus are recorded separately.',
                                'This licence-only release preserves the previously published artwork.')
        readme += ('\nLicence-only update from ' + old_version + '. Texture bytes and runtime\n'
                   'mappings are unchanged. See LICENSE.txt for scope, attribution and exclusions,\n'
                   'and CC-BY-NC-4.0.txt for the complete legal text.\n\n'
                   + notice.decode())
        replacements['README.txt'] = readme.encode()
        receipt_name = old_root + '/receipt.json'
        if receipt_name in original.namelist():
            receipt = json.loads(original.read(receipt_name))
            assert receipt.get('version') == old_version
            receipt.update(version=version, licence='CC BY-NC 4.0',
                           attribution=CREDIT, licence_notice='LICENSE.txt',
                           licence_source_version=old_version,
                           licence_source_archive_sha256=source_sha256)
            replacements['receipt.json'] = (json.dumps(receipt, indent=2) + '\n').encode()
        additions = {'LICENSE.txt': notice, 'CC-BY-NC-4.0.txt': legal}
        if any(old_root + '/' + rel in original.namelist() for rel in additions):
            raise ValueError('Existing licensing file requires explicit migration')
        sources = {info.filename[len(old_root)+1:]: info for info in entries}
        with zipfile.ZipFile(Tee(), 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=1) as target:
            for rel in sorted(set(sources) | set(additions)):
                if rel in additions:
                    data = additions[rel]
                elif rel in replacements:
                    data = replacements[rel]
                    changed.append(rel)
                else:
                    data = original.read(sources[rel])  # Includes ZIP CRC validation.
                    unchanged.append(rel)
                if rel in replacements:
                    assert Path(rel).suffix.lower() not in ('.png', '.dds')
                info = zipfile.ZipInfo(root + '/' + rel, date_time=(2026, 11, 10, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                target.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=1)
                records[rel] = {'sha256': hashlib.sha256(data).hexdigest(), 'size': len(data)}
    descriptor = dict(size=sink.size, unpacked_size=sum(r['size'] for r in records.values()),
                      file_count=len(records), sha256=sink.digest.hexdigest(), root=root)
    return dict(id=mod_id, version=version, source_version=old_version,
                source_archive_sha256=source_sha256, archive=descriptor,
                native_textures=len(before['textures']), wide_entries=len(before.get('wide', {})),
                changed_files=changed, added_files=sorted(additions), unchanged_files=unchanged,
                textures_and_mappings_unchanged=True, files=records)
