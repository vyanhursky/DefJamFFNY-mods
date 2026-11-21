"""Invented fighter recipes/media: no game dump, authored fighter or game assets."""
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import wave
import zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import fighter_check as fc
import package_check as pc


def encoded(value):
    return json.dumps(value).encode()


def descriptor(name, data):
    return {'path': name, 'sha256': hashlib.sha256(data).hexdigest()}


def fixture(audio=False):
    recipe = encoded({'stats': {k: 1 for k in ('upper', 'lower', 'speed', 'toughness', 'health')},
                      'styles': [0], 'caf_values': [0] * 38, 'caf_colors': [0] * 38})
    resources = [{'id': 'caf', 'kind': 'caf', 'compatibility': {},
                  'source': {'format': 'caf-fighter-1', 'selection': descriptor('fighter.json', recipe)}}]
    files = {'fighter.json': recipe, 'README.md': b'Invented test data, not a usable game fighter.'}
    components = {'caf': 'synthetic-fighter/caf'}
    if audio:
        stream = io.BytesIO()
        with wave.open(stream, 'wb') as wav:
            wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(24000)
            wav.writeframes(b'\0\0' * 240)
        raw = stream.getvalue(); files['voice.wav'] = raw
        resources.append({'id': 'voice', 'kind': 'voice', 'compatibility': {'events': 'retail/test'},
                          'source': {'format': 'fighter-voice-1', 'template_voice': 0,
                                     'samples': {}, 'intro': descriptor('voice.wav', raw),
                                     'extro': descriptor('voice.wav', raw)}})
        components['voice'] = 'synthetic-fighter/voice'
    manifest = {'schema': 'fighter-registry-draft-1', 'id': 'synthetic-fighter', 'version': '1.0.0',
                'requires': {}, 'resources': resources, 'overrides': [],
                'fighters': [{'id': 'test', 'name': 'Invented test', 'inherits': 'retail/blaze',
                              'components': components}]}
    files['fighters.json'] = encoded(manifest)
    return files


class FighterPackages(unittest.TestCase):
    def unpack(self, files, root='synthetic-fighter', version='1.0.0'):
        with tempfile.TemporaryDirectory() as temp:
            scratch = Path(temp); archive = scratch / 'fixture.zip'
            with zipfile.ZipFile(archive, 'w') as bundle:
                for name, data in files.items():bundle.writestr(root + '/' + name, data)
            spec = {'root': root, 'size': archive.stat().st_size, 'sha256': pc.sha(archive),
                    'file_count': len(files), 'unpacked_size': sum(map(len, files.values()))}
            return pc.unpack_archive(archive, spec, scratch / 'stage', version=version)

    def test_data_only_caf_and_voice_inventory(self):
        result = self.unpack(fixture(audio=True))
        self.assertEqual(result['capabilities'], ['fighters-v1'])
        self.assertEqual(result['fighter_id'], 'synthetic-fighter')
        self.assertEqual(result['fighter_count'], 1)

    def test_corrupt_declared_file_rejected(self):
        files = fixture(); files['fighter.json'] += b' '
        with self.assertRaisesRegex(ValueError, 'hash differs'):
            self.unpack(files)

    def test_undeclared_data_is_not_admitted_by_extension(self):
        files = fixture(); files['unknown.o'] = b'not an allowed resource'
        with self.assertRaisesRegex(ValueError, 'Undeclared'):
            self.unpack(files)

    def test_host_executables_and_scripts_stay_forbidden(self):
        for name in ('run.py', 'run.exe'):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'Unsupported'):
                self.unpack({**fixture(), name: b'do not run'})

    def test_unknown_pointer_fields_and_traversal_rejected(self):
        for bad in ('pointer', 'path'):
            files = fixture(); manifest = json.loads(files['fighters.json'])
            source = manifest['resources'][0]['source']
            if bad == 'pointer':source['pointer'] = 4096
            else:source['selection']['path'] = '../fighter.json'
            files['fighters.json'] = encoded(manifest)
            with self.subTest(bad=bad), self.assertRaises(ValueError):self.unpack(files)

    def test_duplicate_and_nonfinite_json_rejected(self):
        for raw in (b'{"schema":0,"schema":1}', b'{"value":NaN}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                self.unpack({**fixture(), 'fighters.json': raw})

    def test_identity_and_version_bound_to_archive_record(self):
        for root, version in [('different-root', '1.0.0'), ('synthetic-fighter', '1.0.1')]:
            with self.subTest(root=root, version=version), self.assertRaisesRegex(ValueError, 'differs'):
                self.unpack(fixture(), root=root, version=version)

    def test_fighter_cannot_mix_language_or_texture_manifests(self):
        for name in ('manifest.ini', 'language.ini'):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'cannot mix'):
                self.unpack({**fixture(), name: b'[unused]'})

    def test_wav_data_is_parsed_after_declared_hash_checks(self):
        files = fixture(audio=True); files['voice.wav'] = b'not a wave'
        manifest = json.loads(files['fighters.json']); voice = manifest['resources'][1]['source']
        voice['intro'] = voice['extro'] = descriptor('voice.wav', files['voice.wav'])
        files['fighters.json'] = encoded(manifest)
        with self.assertRaisesRegex(ValueError, 'Invalid fighter WAV'):self.unpack(files)

    def test_missing_or_wrong_validator_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.dict(os.environ, {fc.SOURCE_ENV: temp}):
                with self.assertRaisesRegex(ValueError, 'pinned'):self.unpack(fixture())
        with patch.object(fc.subprocess, 'run') as run:
            run.return_value.stdout = '0' * 40
            with self.assertRaisesRegex(ValueError, 'pinned release'):fc.runtime_source()

    def test_declared_png_is_parsed_not_only_hashed(self):
        files = fixture(); files['portrait.png'] = b'not a png'
        manifest = json.loads(files['fighters.json'])
        manifest['resources'].append({'id': 'portrait', 'kind': 'portrait', 'compatibility': {},
                                     'source': {'format': 'eagl-portrait-png-1', 'donor': 'retail/pockets',
                                                'hd_scale': 1, 'images': {'icon': descriptor('portrait.png', files['portrait.png'])}}})
        files['fighters.json'] = encoded(manifest)
        with self.assertRaisesRegex(ValueError, 'Invalid PNG'):self.unpack(files)
        stream = io.BytesIO(); Image.new('RGBA', (64, 64), 'red').save(stream, format='PNG')
        files['portrait.png'] = stream.getvalue()
        manifest['resources'][-1]['source']['images']['icon'] = descriptor('portrait.png', files['portrait.png'])
        files['fighters.json'] = encoded(manifest)
        self.assertEqual(self.unpack(files)['fighter_count'], 1)

    def test_modified_validator_source_fails_closed(self):
        from subprocess import CompletedProcess
        with patch.object(fc.subprocess, 'run', side_effect=[
                CompletedProcess([], 0, stdout=fc.RUNTIME_COMMIT), CompletedProcess([], 1)]):
            with self.assertRaisesRegex(ValueError, 'local changes'):fc.runtime_source()

    def test_extra_python_source_never_imported(self):
        from subprocess import CompletedProcess
        with tempfile.TemporaryDirectory() as temp:
            setup = Path(temp) / 'setup'; setup.mkdir()
            (setup / 'fighter_packages.py').write_text('raise AssertionError("must not import")')
            (setup / 'rogue.py').write_text('raise AssertionError("must not import")')
            with patch.dict(os.environ, {fc.SOURCE_ENV: temp}), patch.object(fc.subprocess, 'run', side_effect=[
                    CompletedProcess([], 0, stdout=fc.RUNTIME_COMMIT), CompletedProcess([], 0),
                    CompletedProcess([], 0, stdout='setup/fighter_packages.py\n')]):
                with self.assertRaisesRegex(ValueError, 'Unexpected Python source'):fc.runtime_source()


if __name__ == '__main__':unittest.main()
