import base64
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import release
import package_check
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from PIL import Image
sys.path.pop(0)


class ReleaseTests(unittest.TestCase):
    def test_empty_release_signs_only_with_reviewed_pin(self):
        with tempfile.TemporaryDirectory() as scratch:
            root=Path(scratch);(root/'mods').mkdir()
            key=Ed25519PrivateKey.generate()
            (root/'catalogue-keys.json').write_text(json.dumps({'keys':[key.public_key().public_bytes_raw().hex()]}))
            out=root/'dist'
            with patch.object(release,'ROOT',root),patch.object(release,'previous_index',return_value={'revision':3,'mods':[]}),patch.dict('os.environ',CATALOGUE_ED25519_KEY=base64.b64encode(key.private_bytes_raw()).decode()),patch('sys.argv',['release','prepare','--out',str(out)]):
                release.main()
                self.assertFalse((out/'index.json.sig').exists())
                with patch('sys.argv',['release','sign','--out',str(out)]):release.main()
            raw=(out/'index.json').read_bytes()
            key.public_key().verify((out/'index.json.sig').read_bytes(),raw)
            self.assertEqual(json.loads(raw)['revision'],4)
            self.assertEqual(json.loads(raw)['mods'],[])

    def test_missing_key_fails_closed(self):
        with tempfile.TemporaryDirectory() as scratch:
            root=Path(scratch);(root/'catalogue-keys.json').write_text('{"keys":[]}')
            with patch.object(release,'ROOT',root),patch('sys.argv',['release','prepare','--out',str(root/'dist')]):
                with self.assertRaises(ValueError):release.main()
            self.assertFalse((root/'dist').exists())

    def test_actual_synthetic_zip_is_validated(self):
        with tempfile.TemporaryDirectory() as scratch:
            root=Path(scratch);png=io.BytesIO();Image.new('RGBA',(8,8),'red').save(png,format='PNG')
            entries={'test/manifest.ini':('[pack]\nschema=1\n[textures]\n'+'a'*64+'=textures/paper.png\n').encode(),
                     'test/textures/paper.png':png.getvalue()}
            source=root/'pack.zip'
            with zipfile.ZipFile(source,'w') as archive:
                for name,data in entries.items():archive.writestr(name,data)
            descriptor=dict(root='test',size=source.stat().st_size,sha256=package_check.sha(source),
                unpacked_size=sum(map(len,entries.values())),file_count=2)
            result=package_check.unpack_archive(source,descriptor,root/'stage')
            self.assertEqual(result['texture_ids'],['a'*64])
            self.assertEqual(result['capabilities'],['textures-v1'])


if __name__=='__main__':unittest.main()


class HistoryAvailabilityTests(unittest.TestCase):
    def test_unexpected_404_never_resets_history(self):
        import urllib.error
        error=urllib.error.HTTPError('https://example.invalid',404,'missing',{},None)
        with patch.object(release,'get',side_effect=error):
            with self.assertRaisesRegex(ValueError,'history missing'):release.previous_index([])
            self.assertEqual(release.previous_index([],bootstrap=True)['revision'],0)


class BootstrapTests(unittest.TestCase):
    def test_explicit_bootstrap_verifies_nonempty_first_catalogue(self):
        with tempfile.TemporaryDirectory() as scratch:
            root=Path(scratch); (root/'mods').mkdir()
            (root/'catalogue-keys.json').write_text('{"keys":["'+'a'*64+'"]}')
            # Metadata is already covered by contract tests; verify the release
            # path scans first-publication rows rather than skipping validation.
            rows=[{'id':'fixture'}]
            with patch.object(release,'ROOT',root),patch.object(release.catalogue,'load_mods',return_value=rows),patch.object(release.catalogue,'validate_history'),patch.object(release.catalogue,'build',return_value=b'{}'),patch.object(release,'previous_index',return_value={'revision':0,'mods':[]}),patch.object(release,'verify_downloads') as verify,patch('sys.argv',['release','prepare','--bootstrap','--out',str(root/'out')]):
                release.main()
                verify.assert_called_once_with(rows)
            with patch.object(release,'ROOT',root),patch.object(release.catalogue,'load_mods',return_value=rows),patch.object(release,'previous_index',return_value={'revision':1,'mods':[]}),patch('sys.argv',['release','prepare','--bootstrap','--out',str(root/'other')]):
                with self.assertRaisesRegex(ValueError,'no signed catalogue'):
                    release.main()
