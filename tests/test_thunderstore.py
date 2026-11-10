"""Thunderstore uploads: deterministic packaging, verifier acceptance and catalogue append."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import catalogue
import package_check as pc
import thunderstore as ts
sys.path.pop(0)
ID = 'a' * 64


def png(size, color='red'):
    out = io.BytesIO()
    Image.new('RGBA', size, color).save(out, format='PNG')
    return out.getvalue()


class Fixture:
    def __init__(self, root):
        self.root = root
        self.mods = root / 'mods'; self.mods.mkdir()
        self.source = root / 'paper-v1-0-0.zip'
        entries = {'paper-v1-0-0/manifest.ini': f'[pack]\nschema=1\n[textures]\n{ID}=textures/a.png\n'.encode(),
                   'paper-v1-0-0/textures/a.png': png((8, 8))}
        with zipfile.ZipFile(self.source, 'w') as bundle:
            for name, data in entries.items():
                bundle.writestr(name, data)
        self.icon = root / 'icon-source.png'; self.icon.write_bytes(png((512, 512), 'blue'))
        archive = dict(urls=['https://example.invalid/paper.zip'], size=self.source.stat().st_size,
                       unpacked_size=sum(map(len, entries.values())), file_count=2,
                       sha256=pc.sha(self.source), root='paper-v1-0-0')
        self.mod = {'id': 'paper', 'name': "Paper's HD Menus", 'description': 'Synthetic fixture. ' * 30,
                    'authors': ['Test'], 'class': 'original', 'licence': 'Test fixture',
                    'homepage': 'https://example.invalid/paper', 'revoked_versions': [],
                    'versions': [dict(version='1.0.0', channel='stable', min_recomp='0.12.1',
                                      capabilities=['textures-v1'], reviewed='2026-11-01', depends=[],
                                      conflicts=[], load_after=['faithful-hd'], archive=archive)]}
        (self.mods / 'paper.json').write_text(json.dumps(self.mod, indent=2) + '\n')

    def pack(self, *extra, out='dist'):
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            ts.main(['pack', '--mod', 'paper', '--version', '1.0.1', '--source', str(self.source),
                     '--icon', str(self.icon), '--mods', str(self.mods), '--out', str(self.root / out), *extra])
        return json.loads(printed.getvalue())


class ThunderstorePackaging(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.fx = Fixture(Path(self.scratch.name))

    def tearDown(self):
        self.scratch.cleanup()

    def test_upload_layout_and_record(self):
        result = self.fx.pack()
        upload = Path(result['upload'])
        self.assertEqual(upload.name, 'DefJamRecompiled-Papers_HD_Menus-1.0.1.zip')
        with zipfile.ZipFile(upload) as bundle:
            names = bundle.namelist()
            manifest = json.loads(bundle.read('manifest.json'))
            readme = bundle.read('README.md').decode()
            icon = Image.open(io.BytesIO(bundle.read('icon.png')))
        self.assertEqual(names, ['README.md', 'icon.png', 'manifest.json',
                                 'paper-v1-0-0/manifest.ini', 'paper-v1-0-0/textures/a.png'])
        self.assertEqual(icon.size, (256, 256))
        self.assertEqual(manifest['version_number'], '1.0.1')
        self.assertLessEqual(len(manifest['description']), 250)
        self.assertIn('`paper-v1-0-0` folder', readme)
        version = result['version']
        self.assertEqual(version['capabilities'], ['textures-v1', pc.STOREFRONT])
        self.assertEqual(version['load_after'], ['faithful-hd'])
        self.assertEqual(version['archive']['urls'],
                         ['https://thunderstore.io/package/download/DefJamRecompiled/Papers_HD_Menus/1.0.1/'])
        self.assertEqual((version['archive']['file_count'], version['archive']['root']), (2, 'paper-v1-0-0'))

    def test_output_is_deterministic(self):
        first = self.fx.pack(out='one')['version']['archive']['sha256']
        second = self.fx.pack(out='two')['version']['archive']['sha256']
        self.assertEqual(first, second)

    def test_append_keeps_history_and_validates(self):
        before = json.loads((self.fx.mods / 'paper.json').read_text())
        self.fx.pack('--append', '--mirror', 'https://mirror.invalid/paper-1.0.1.zip')
        rows = catalogue.load_mods(self.fx.mods)
        catalogue.validate_history(rows, {'mods': [before]})
        self.assertEqual([v['version'] for v in rows[0]['versions']], ['1.0.0', '1.0.1'])
        self.assertEqual(len(rows[0]['versions'][1]['archive']['urls']), 2)

    def test_rejections(self):
        for argv, message in [(['--version', '1.0.0'], 'immutable'),
                              (['--version', '1.1.0-rc.1'], 'without a suffix'),
                              (['--name', 'Has Space'], 'Invalid Thunderstore name'),
                              (['--description', 'x' * 251], '250')]:
            with self.subTest(argv=argv), self.assertRaisesRegex(ValueError, message):
                self.fx.pack(*argv)
        self.fx.icon.write_bytes(png((300, 200)))
        with self.assertRaisesRegex(ValueError, 'square'):
            self.fx.pack()

    def test_verifier_needs_the_capability_for_root_files(self):
        version = self.fx.pack()['version']
        upload = next((self.fx.root / 'dist').glob('*.zip'))
        with self.assertRaisesRegex(ValueError, 'archive root'):
            pc.unpack_archive(upload, version['archive'], self.fx.root / 'plain')
        with self.assertRaisesRegex(ValueError, 'differs from the catalogue'):
            pc.unpack_archive(upload, version['archive'], self.fx.root / 'other', storefront=True, version='2.0.0')

    def test_names_and_descriptions(self):
        self.assertEqual(ts.package_name("ZARF's Spanish Translation mod"), 'ZARFs_Spanish_Translation_mod')
        self.assertEqual(ts.package_name('HD Menus and UI'), 'HD_Menus_and_UI')
        sentence = 'A first sentence long enough to stand alone as a listing summary, ' * 2 + 'end.'
        self.assertEqual(ts.short_description(sentence + ' ' + 'word ' * 80), sentence)
        self.assertLessEqual(len(ts.short_description('word ' * 80)), 250)


if __name__ == '__main__':
    unittest.main()
