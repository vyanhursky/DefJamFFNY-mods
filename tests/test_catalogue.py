import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('catalogue', ROOT / 'tools/catalogue.py')
catalogue = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalogue)


def fixture():
    # Synthetic metadata only. Never publish this test package.
    return dict(id='test-paper', name='Test paper', description='Synthetic test', authors=['Test'],
                licence='Test only', homepage='https://example.invalid/test',
                **{'class': 'original'}, revoked_versions=[], versions=[dict(
                    version='1.0.0', channel='stable', min_recomp='0.1.0', capabilities=['textures-v1'],
                    reviewed='2026-10-21', depends=[], conflicts=[], load_after=[], archive=dict(
                        urls=['https://example.invalid/test.zip'], size=200, unpacked_size=100,
                        file_count=2, sha256='a' * 64, root='test-paper'))])


class CatalogueTests(unittest.TestCase):
    def test_valid_fixture(self):
        self.assertEqual(catalogue.validate_mod(fixture())['id'], 'test-paper')

    def test_deterministic_sorted_bytes(self):
        first, second = fixture(), fixture()
        second['id'] = 'another-paper'
        args = (2, '2026-10-21T00:00:00Z', '2026-11-21T00:00:00Z')
        data = catalogue.build([first, second], *args)
        self.assertEqual(data, catalogue.build([second, first], *args))
        self.assertEqual(json.loads(data)['mods'][0]['id'], 'another-paper')

    def test_empty_bootstrap_is_supported(self):
        data = catalogue.build([], 1, '2026-10-21T00:00:00Z', '2026-11-21T00:00:00Z')
        self.assertEqual(json.loads(data)['mods'], [])

    def test_invalid_header(self):
        for revision, issued, expires in [
                (True, '2026-10-21T00:00:00Z', '2026-11-21T00:00:00Z'),
                (0, '2026-10-21T00:00:00Z', '2026-11-21T00:00:00Z'),
                (1, '2026-10-21T00:00:00Z', '2026-10-20T00:00:00Z'),
                (1, '2026-10-21T00:00:00+00:00', '2026-11-21T00:00:00Z')]:
            with self.subTest(revision=revision, issued=issued, expires=expires):
                with self.assertRaises(ValueError):
                    catalogue.build([], revision, issued, expires)

    def test_rejects_bad_fields(self):
        mutations = [
            lambda m: m.update(unexpected=True),
            lambda m: m.update(id='../test'),
            lambda m: m.update(authors=[]),
            lambda m: m.update(homepage='http://example.invalid'),
            lambda m: m.update(homepage='https://user:password@example.invalid'),
            lambda m: m.update(homepage='https://example.invalid:bad'),
            lambda m: m.update(revoked_versions=['9.0.0']),
            lambda m: m['versions'].append(copy.deepcopy(m['versions'][0])),
            lambda m: m['versions'][0].update(version='1.0.0-01', channel='prerelease'),
            lambda m: m['versions'][0].update(version='1.0.0-rc1'),
            lambda m: m['versions'][0].update(reviewed='2026-02-30'),
            lambda m: m['versions'][0].update(depends=['test-paper']),
            lambda m: m['versions'][0].update(depends=['other'], conflicts=['other']),
            lambda m: m['versions'][0]['archive'].update(size=True),
            lambda m: m['versions'][0]['archive'].update(unpacked_size=0),
            lambda m: m['versions'][0]['archive'].update(sha256='x' * 64),
            lambda m: m['versions'][0]['archive'].update(root='..'),
            lambda m: m['versions'][0]['archive'].update(urls=[]),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                value = fixture()
                mutate(value)
                with self.assertRaises(ValueError):
                    catalogue.validate_mod(value)

    def test_file_identity_and_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as scratch:
            path = Path(scratch) / 'other.json'
            path.write_text(json.dumps(fixture()), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Filename'):
                catalogue.load_mods(scratch)
            path.unlink()
            path = Path(scratch) / 'test-paper.json'
            path.write_text('{"id":"first","id":"second"}', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Duplicate JSON'):
                catalogue.load_mods(scratch)

    def test_symlink_metadata_is_rejected(self):
        with tempfile.TemporaryDirectory() as scratch:
            target = Path(scratch) / 'target'
            target.write_text(json.dumps(fixture()), encoding='utf-8')
            (Path(scratch) / 'test-paper.json').symlink_to(target)
            with self.assertRaisesRegex(ValueError, 'Unsafe metadata'):
                catalogue.load_mods(scratch)


if __name__ == '__main__':
    unittest.main()
