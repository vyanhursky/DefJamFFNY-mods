import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import relicense_hd_packs as licensing
import hashlib
from PIL import Image
import package_check

class LicensingTests(unittest.TestCase):
    def test_deterministic_archive_preserves_payload_and_runtime_contract(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'source.zip'
            image = io.BytesIO()
            Image.new('RGBA', (2, 2), (50, 100, 150, 128)).save(image, format='PNG')
            texture = image.getvalue()
            manifest = '[pack]\nschema=1\nname=HD Example 1.0.0\npng_mips=channels\n[textures]\n' + 'a'*64 + '=textures/a.png\n[wide]\n' + 'a'*64 + '=stretch\n'
            with zipfile.ZipFile(source, 'w') as z:
                for rel, data in {'manifest.ini': manifest.encode(), 'README.txt': b'HD Example 1.0.0',
                                  'textures/a.png': texture,
                                  'receipt.json': json.dumps({'version':'1.0.0','native_verified':False}).encode()}.items():
                    z.writestr('example-v1-0-0/' + rel, data)
            pin = hashlib.sha256(source.read_bytes()).hexdigest()
            kwargs = dict(mod_id='example', name='HD Example', old_version='1.0.0', version='1.0.1', source_sha256=pin)
            a, b = io.BytesIO(), io.BytesIO()
            receipt = licensing.repackage(source, a, **kwargs)
            self.assertEqual(receipt, licensing.repackage(source, b, **kwargs))
            self.assertEqual(a.getvalue(), b.getvalue())
            self.assertEqual(hashlib.sha256(a.getvalue()).hexdigest(), receipt['archive']['sha256'])
            with zipfile.ZipFile(a) as z:
                root = receipt['archive']['root'] + '/'
                self.assertIsNone(z.testzip())
                self.assertEqual(z.read(root+'textures/a.png'), texture)
                updated = licensing.manifest_sections(z.read(root+'manifest.ini'))
                before = licensing.manifest_sections(manifest.encode())
                self.assertEqual(updated['textures'], before['textures'])
                self.assertEqual(updated['wide'], before['wide'])
                self.assertEqual(updated['pack']['png_mips'], 'channels')
                self.assertEqual(updated['pack']['name'], 'HD Example 1.0.1')
                self.assertIn(licensing.CREDIT.encode(), z.read(root+'LICENSE.txt'))
                self.assertEqual(z.read(root+'CC-BY-NC-4.0.txt'), licensing.LEGAL.read_bytes())
                self.assertFalse(json.loads(z.read(root+'receipt.json'))['native_verified'])
                self.assertEqual(len(z.infolist()), receipt['archive']['file_count'])
                self.assertEqual(sum(i.file_size for i in z.infolist()), receipt['archive']['unpacked_size'])
            target = Path(folder) / 'updated.zip'
            target.write_bytes(a.getvalue())
            installed = package_check.unpack_archive(target, receipt['archive'], Path(folder) / 'installed')
            self.assertEqual(installed['texture_ids'], ['a'*64])
            self.assertEqual(installed['wide_ids'], ['a'*64])
            with self.assertRaisesRegex(ValueError, 'published pin'):
                licensing.repackage(source, io.BytesIO(), **dict(kwargs,source_sha256='0'*64))
