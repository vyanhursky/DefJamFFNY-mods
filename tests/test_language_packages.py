"""Synthetic language/HD package acceptance and malformed-input rejection."""
import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import package_check as pc


class LanguagePackages(unittest.TestCase):
    def entries(self, images=False):
        values = {
            'language.ini': b'[language]\nschema=1\nname=Test\nlanguage=it\n[files]\nassets/misc.viv|cmusen.loc=patches/001.djd\n',
            'patches/001.djd': b'DJDELTA1synthetic-format-test-only',
            'CREDITS.md': b'Synthetic credits; no game data.',
        }
        if images:
            png = io.BytesIO()
            Image.new('RGBA', (8, 8), 'red').save(png, format='PNG')
            values.update({'manifest.ini': ('[pack]\nschema=1\n[textures]\n' + 'a'*64 + '=textures/a.png\n').encode(), 'textures/a.png': png.getvalue()})
        return values

    def unpack(self, values):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            source = root/'pack.zip'
            with zipfile.ZipFile(source, 'w') as archive:
                for name, data in values.items():
                    archive.writestr('test-language/'+name, data)
            descriptor = dict(root='test-language', size=source.stat().st_size,
                              sha256=pc.sha(source), unpacked_size=sum(map(len, values.values())), file_count=len(values))
            return pc.unpack_archive(source, descriptor, root/'stage')

    def test_language_with_credits_and_deltas(self):
        self.assertEqual(self.unpack(self.entries())['capabilities'], ['language-v1'])

    def test_language_with_hd_images_requires_both_capabilities(self):
        result = self.unpack(self.entries(True))
        self.assertEqual(result['capabilities'], ['language-v1', 'textures-v1'])
        self.assertEqual(result['texture_ids'], ['a'*64])

    def test_bad_language_deltas_and_targets_fail(self):
        original = self.entries()
        for before, after in [
                (b'patches/001.djd', b'../001.djd'),
                (b'assets/misc.viv|cmusen.loc', b'assets/../misc.viv|cmusen.loc'),
                (b'schema=1', b'schema=2'),
                (b'patches/001.djd', b'patches/missing.djd')]:
            with self.subTest(after=after):
                values = dict(original)
                values['language.ini'] = values['language.ini'].replace(before, after)
                with self.assertRaises(ValueError):
                    self.unpack(values)
        values = dict(original)
        values['patches/001.djd'] = b'NOTDELTA'
        with self.assertRaises(ValueError):
            self.unpack(values)

    def test_case_duplicate_target_rejected(self):
        values = self.entries()
        values['language.ini'] += b'ASSETS/MISC.VIV|CMUSEN.LOC=patches/001.djd\n'
        with self.assertRaisesRegex(ValueError, 'listed twice'):
            self.unpack(values)

    def test_language_hd_images_are_actually_checked(self):
        values = self.entries(True)
        values['textures/a.png'] = b'not an image'
        with self.assertRaises(ValueError):
            self.unpack(values)

    def test_executable_extension_remains_forbidden(self):
        values = self.entries()
        values['run.py'] = b'print("never execute")'
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            self.unpack(values)


if __name__ == '__main__':
    unittest.main()
