"""Texture ZIP verifier, kept aligned with the game helper's schema-1 contract.

Source: DefJamFFNY-recomp/setup/mods.py. No asset bytes are stored here.
"""
import configparser
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import struct
import zipfile
import catalogue as contract
MAX_FILE = 512 * 1024**2
MAX_ARCHIVE = 8 * 1024**3
MAX_FILES = 65536
ALLOWED = {'.ini', '.png', '.dds', '.json', '.txt'}

class ModError(ValueError):
    pass

def check(value, message):
    if not value:
        raise ModError(message)

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def linked(path):
    path = Path(path)
    return path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction())

def sync_directory(path):
    if os.name != 'nt':
        fd = os.open(path, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

def safe_relative(value):
    check(isinstance(value, str) and 0 < len(value) < 900 and '..' not in value,
          'Unsafe relative path')
    check(re.fullmatch(r'[A-Za-z0-9_./-]+', value), 'Unsupported path characters')
    parts = PurePosixPath(value).parts
    check(parts and not value.startswith('/') and all(p not in ('.', '..') and not p.startswith('.') for p in parts),
          'Unsafe relative path')
    # Windows aliases, device names, trailing dots/spaces and case collisions are unsafe on every host.
    reserved = {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}
    check(all(not p.endswith('.') and p.split('.')[0].upper() not in reserved for p in parts), 'Reserved path')
    check('/'.join(parts) == value, 'Noncanonical path')
    return parts

def image_shape(path, png_only=False):
    with Path(path).open('rb') as stream:
        head = stream.read(128)
    if Path(path).suffix.lower() == '.png':
        check(head[:8] == b'\x89PNG\r\n\x1a\n' and len(head) >= 33 and head[12:16] == b'IHDR', 'Invalid PNG')
        from PIL import Image
        with Image.open(path) as picture:
            check(picture.format == 'PNG' and not getattr(picture, 'is_animated', False), 'Unsupported PNG')
            w, h = picture.size
            check(0 < w <= 16384 and 0 < h <= 16384 and w * h <= 64 * 1024**2, 'Image dimensions exceed limits')
            picture.verify()
        return w, h
    check(not png_only and Path(path).suffix.lower() == '.dds' and len(head) == 128 and head[:4] == b'DDS ', 'Unsupported image')
    size, flags, h, w = struct.unpack_from('<4I', head, 4)
    check(size == 124 and 0 < w <= 16384 and 0 < h <= 16384 and w * h <= 64 * 1024**2, 'Invalid DDS dimensions')
    check(struct.unpack_from('<I', head, 76)[0] == 32 and head[84:88] in (b'DXT1', b'DXT3', b'DXT5'), 'Unsupported DDS format')
    mips = max(1, struct.unpack_from('<I', head, 28)[0])
    check(mips <= 15 and mips <= max(w, h).bit_length(), 'Invalid DDS mip count')
    check(struct.unpack_from('<I', head, 112)[0] == 0 and struct.unpack_from('<I', head, 24)[0] <= 1 and struct.unpack_from('<I', head, 80)[0] & 4, 'DDS cube/volume unsupported')
    block = 8 if head[84:88] == b'DXT1' else 16
    expected = 128
    for _ in range(mips):
        expected += max(1, (w + 3)//4) * max(1, (h + 3)//4) * block
        w, h = max(1, w//2), max(1, h//2)
    check(Path(path).stat().st_size == expected, 'Invalid DDS payload size')
    return struct.unpack_from('<I', head, 16)[0], struct.unpack_from('<I', head, 12)[0]

def validate_pack(folder):
    manifest = folder / 'manifest.ini'
    check(manifest.is_file() and not manifest.is_symlink() and manifest.stat().st_size <= 16 * 1024**2,
          'Missing/oversized manifest')
    raw = manifest.read_text(encoding='utf-8-sig')
    check(all(len(line.encode('utf-8')) < 1900 for line in raw.splitlines()), 'Manifest line too long')
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    parser.optionxform = str
    parser.read_string(raw)
    check(not parser.defaults() and set(parser.sections()) <= {'pack', 'textures', 'wide'}, 'Unsupported manifest section')
    check(parser.get('pack', 'schema', fallback='') == '1', 'Unsupported manifest schema')
    check(parser.get('pack', 'png_mips', fallback='opacity') in ('channels', 'opacity'), 'Invalid PNG mip policy')
    check(parser.has_section('textures') and 0 < len(parser['textures']) <= MAX_FILES, 'Missing texture entries')
    refs, dimensions = set(), {}
    def reference(value, png_only=False):
        safe_relative(value)
        path = folder.joinpath(*PurePosixPath(value).parts)
        check(path.is_file() and not linked(path), 'Missing image: ' + value)
        dims = image_shape(path, png_only)
        refs.add(value)
        return dims
    for key, value in parser['textures'].items():
        check(re.fullmatch('[0-9a-f]{64}', key), 'Invalid texture ID')
        dimensions[key] = reference(value)
    if parser.has_section('wide'):
        for key, value in parser['wide'].items():
            check(re.fullmatch('[0-9a-f]{64}', key), 'Invalid wide anchor ID')
            if value == 'stretch':
                continue  # Runtime can stretch a live/original overlay without replacing its pixels.
            check(key in dimensions, 'Wide slab anchor has no texture entry')
            slabs = value.split(';')
            check(0 < len(slabs) <= 16, 'Too many wide slabs')
            for slab in slabs:
                shift, separator, relative = slab.partition(':')
                check(separator and (shift == 'inner' or re.fullmatch(r'-?[0-9]+', shift)), 'Invalid wide shift')
                check(shift == 'inner' or -16384 <= int(shift) <= 16384, 'Wide shift exceeds limits')
                check(reference(relative, True) == dimensions[key], 'Wide slab/anchor dimensions differ')
    return {'capabilities': ['textures-v1'] + (['wide-v1'] if parser.has_section('wide') else []),
            'texture_ids': list(dimensions), 'wide_ids': list(parser['wide']) if parser.has_section('wide') else []}

def unpack_archive(archive, descriptor, destination, cancelled=lambda: None):
    check(Path(archive).stat().st_size == descriptor['size'] and sha(archive) == descriptor['sha256'],
          'Package size or SHA-256 mismatch')
    check(descriptor['size'] <= MAX_ARCHIVE and descriptor['unpacked_size'] <= 16 * 1024**3
          and descriptor['file_count'] <= MAX_FILES, 'Package exceeds installer limits')
    root = descriptor['root']
    contract.slug(root)
    files, seen, size = [], set(), 0
    with zipfile.ZipFile(archive) as bundle:
        check(len(bundle.infolist()) <= MAX_FILES * 2, 'Too many archive entries')
        for row in bundle.infolist():
            cancelled()
            name = row.filename[:-1] if row.is_dir() else row.filename
            parts = safe_relative(name)
            check(parts[0] == root, 'Unexpected archive root')
            folded = name.casefold()
            check(folded not in seen, 'Duplicate/case-colliding archive path')
            seen.add(folded)
            mode = row.external_attr >> 16
            check(not row.flag_bits & 1 and stat.S_IFMT(mode) in (0, stat.S_IFREG, stat.S_IFDIR), 'Links/encrypted/special entries forbidden')
            if row.is_dir():
                continue
            check(len(parts) > 1 and PurePosixPath(name).suffix.lower() in ALLOWED
                  and row.file_size <= MAX_FILE, 'Unsupported/oversized archive file')
            size += row.file_size
            files.append((row, parts[1:]))
        check(len(files) == descriptor['file_count'] and size == descriptor['unpacked_size'], 'Unpacked size/file-count mismatch')
        check(shutil.disk_usage(destination.parent).free >= size + 32 * 1024**2, 'Not enough free space to install')
        destination.mkdir()
        hashes = {}
        for row, parts in files:
            cancelled()
            target = destination.joinpath(*parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open(row) as source, target.open('xb') as output:
                copied = 0
                while chunk := source.read(1024 * 1024):
                    cancelled()
                    copied += len(chunk)
                    check(copied <= row.file_size, 'Archive expansion exceeds declared size')
                    output.write(chunk)
                output.flush()
                os.fsync(output.fileno())
            check(copied == row.file_size, 'Truncated archive entry')
            hashes['/'.join(parts)] = sha(target)
        for directory in sorted((p for p in destination.rglob('*') if p.is_dir()),
                                key=lambda p: len(p.parts), reverse=True):
            sync_directory(directory)
        sync_directory(destination)
        pack = validate_pack(destination)
    return dict(files=hashes, **pack)
