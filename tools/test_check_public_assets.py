"""Synthetic fixtures only: no real credentials, personal paths or external data."""
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest
from unittest import mock
import zipfile
import zlib

spec = importlib.util.spec_from_file_location('preflight', Path(__file__).with_name('check_public_assets.py'))
pf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pf)
FAKE_PATH = ('/' + 'workspace/' + 'synthetic-example/asset.blend').encode()
FAKE_TOKEN = ('gh' + 'p_' + 'NOTAREALCREDENTIAL' * 2).encode()


def chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)


def png(*parts):
    return b'\x89PNG\r\n\x1a\n' + b''.join(chunk(*p) for p in parts) + chunk(b'IEND', b'')


def exr(value):
    return b'v/1\x01' + struct.pack('<I', 2) + b'File\0string\0' + struct.pack('<I', len(value)) + value + b'\0'


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def codes(self, name, data):
        return {code for _, code in pf.inspect_file(self.put(name, data))}

    def test_clean_source_and_encoder(self):
        self.assertEqual(self.codes('source.py', b'api_token = None\n# schema field: password\n'), set())
        self.assertEqual(self.codes('a.png', png((b'tEXt', b'Software\0Lavf61.7.103'))), set())

    def test_text_patterns_redacted(self):
        self.put('source.txt', FAKE_PATH + b'\n' + FAKE_TOKEN)
        report = pf.audit(self.root)
        output = json.dumps(report).encode()
        self.assertNotIn(FAKE_PATH, output)
        self.assertNotIn(FAKE_TOKEN, output)
        self.assertEqual({v['code'] for v in report['findings']}, {'private_absolute_path_pattern', 'credential_like_pattern'})

    def test_png_plain_compressed_and_international(self):
        variants = [(b'tEXt', b'File\0' + FAKE_PATH),
                    (b'zTXt', b'File\0\0' + zlib.compress(FAKE_PATH)),
                    (b'iTXt', b'File\0\x01\x00en\0label\0' + zlib.compress(FAKE_PATH)),
                    (b'iTXt', b'File\0\x00\x00\0\0' + FAKE_PATH)]
        for variant in variants:
            self.assertIn('private_absolute_path_pattern', self.codes('a.png', png(variant)))

    def test_png_c2pa_manual_without_disclosure_or_mutation(self):
        raw = png((b'caBX', b'synthetic provenance ' + FAKE_TOKEN + FAKE_PATH))
        path = self.put('provenance.png', raw)
        report = pf.audit(self.root)
        self.assertEqual(report['findings'], [{'file': 'provenance.png', 'level': 'manual', 'code': 'png_c2pa_provenance_requires_review'}])
        self.assertNotIn(FAKE_TOKEN.decode(), json.dumps(report))
        self.assertNotIn(FAKE_PATH.decode(), json.dumps(report))
        self.assertEqual(path.read_bytes(), raw)
        self.assertEqual(self.codes('clean.png', png()), set())

    def test_png_decompression_limit_and_crc(self):
        bomb = zlib.compress(b'A' * (pf.MAX_METADATA + 1))
        self.assertIn('metadata_incomplete_invalid_or_limit_reached', self.codes('a.png', png((b'zTXt', b'X\0\0' + bomb))))
        bad = bytearray(png((b'tEXt', b'X\0text')))
        bad[20] ^= 1
        self.assertIn('metadata_incomplete_invalid_or_limit_reached', self.codes('a.png', bytes(bad)))

    def test_png_accumulated_decoded_limit(self):
        part = (b'zTXt', b'X\0\0' + zlib.compress(b'A' * 600000))
        self.assertIn('metadata_incomplete_invalid_or_limit_reached', self.codes('a.png', png(part, part)))

    def test_png_exif_and_truncation_not_clean(self):
        self.assertIn('png_exif_requires_structured_review', self.codes('a.png', png((b'eXIf', b'II\x2a\0'))))
        self.assertIn('metadata_incomplete_invalid_or_limit_reached', self.codes('a.png', b'\x89PNG\r\n\x1a\n'))

    def test_exr_paths_and_clean_untitled(self):
        self.assertIn('absolute_exr_file_attribute', self.codes('a.exr', exr(FAKE_PATH)))
        self.assertIn('absolute_exr_file_attribute', self.codes('a.exr', exr(b'Q:\\synthetic\\a.blend')))
        self.assertEqual(self.codes('a.exr', exr(b'<untitled>    ')), set())

    def test_exr_oversize_and_multipart(self):
        self.assertIn('metadata_incomplete_invalid_or_limit_reached', self.codes('a.exr', b'v/1\x01' + struct.pack('<I', 0x1002)))
        data = b'v/1\x01' + struct.pack('<I', 2) + b'File\0string\0' + struct.pack('<I', pf.MAX_METADATA + 1)
        self.assertIn('metadata_incomplete_invalid_or_limit_reached', self.codes('a.exr', data))

    def test_cad_xml_path_and_no_extraction(self):
        path = self.root / 'a.FCStd'
        with zipfile.ZipFile(path, 'w') as archive:
            archive.writestr('Document.xml', b'<doc><value>' + FAKE_PATH + b'</value></doc>')
            archive.writestr('../outside.txt', b'not extracted')
        codes = {v for _, v in pf.inspect_file(path)}
        self.assertIn('private_absolute_path_pattern', codes)
        self.assertIn('unsafe_cad_member_name', codes)
        self.assertIn('cad_binary_geometry_and_properties_need_native_review', codes)
        self.assertFalse((self.root.parent / 'outside.txt').exists())

    def test_cad_xml_numeric_entities(self):
        path = self.root / 'a.FCStd'
        with zipfile.ZipFile(path, 'w') as archive:
            archive.writestr('Document.xml', b'<doc path="&#47;' + FAKE_PATH[1:] + b'"/>')
        self.assertIn(('finding', 'private_absolute_path_pattern'), pf.inspect_file(path))

    def test_windows_user_path(self):
        value = b'C:\\' + b'Users\\' + b'SyntheticExample\\asset.blend'
        self.assertIn('private_absolute_path_pattern', self.codes('source.txt', value))

    def test_cad_xml_and_directory_limits(self):
        path = self.root / 'a.FCStd'
        with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('Document.xml', b'A' * (pf.MAX_METADATA + 1))
        self.assertIn(('manual', 'metadata_incomplete_invalid_or_limit_reached'), pf.inspect_file(path))
        with zipfile.ZipFile(path, 'w') as archive:
            for i in range(513):
                archive.writestr(str(i), b'')
        self.assertIn(('manual', 'metadata_incomplete_invalid_or_limit_reached'), pf.inspect_file(path))

    def test_zip64_rejected_before_archive_parser(self):
        locator = b'PK\x06\x07' + struct.pack('<IQI', 0, 0, 1)
        end = b'PK\x05\x06' + struct.pack('<4H2IH', 0, 0, 0, 0, 0, 0, 0)
        path = self.put('zip64.FCStd', locator + end)
        with mock.patch.object(pf.zipfile, 'ZipFile') as parser:
            self.assertIn(('manual', 'metadata_incomplete_invalid_or_limit_reached'), pf.inspect_file(path))
            parser.assert_not_called()

    def test_zip64_maximum_comment_rejected(self):
        locator = b'PK\x06\x07' + struct.pack('<IQI', 0, 0, 1)
        end = b'PK\x05\x06' + struct.pack('<4H2IH', 0, 0, 0, 0, 0, 0, 65535)
        path = self.put('zip64.FCStd', locator + end + b'C' * 65535)
        with mock.patch.object(pf.zipfile, 'ZipFile') as parser:
            self.assertIn(('manual', 'metadata_incomplete_invalid_or_limit_reached'), pf.inspect_file(path))
            parser.assert_not_called()

    def test_inaccessible_walk_is_incomplete(self):
        def denied(*args, **kwargs):
            kwargs['onerror'](PermissionError('synthetic unavailable subtree'))
            return iter(())
        with mock.patch.object(pf.os, 'walk', side_effect=denied):
            with self.assertRaises(pf.Incomplete):
                pf.audit(self.root)

    def test_xml_declarations_manual(self):
        path = self.root / 'a.FCStd'
        with zipfile.ZipFile(path, 'w') as archive:
            archive.writestr('Document.xml', b'<!DOCTYPE doc [<!ENTITY sample "x">]><doc>&sample;</doc>')
        self.assertIn(('manual', 'xml_declarations_not_parsed'), pf.inspect_file(path))

    def test_utf16_xml_declarations_manual(self):
        path = self.root / 'a.FCStd'
        with zipfile.ZipFile(path, 'w') as archive:
            archive.writestr('Document.xml', '<!DOCTYPE doc [<!ENTITY sample "x">]><doc>&sample;</doc>'.encode('utf-16'))
        self.assertIn(('manual', 'xml_declarations_not_parsed'), pf.inspect_file(path))

    def test_unsupported_and_native(self):
        self.assertIn('blend_requires_native_read_only_audit', self.codes('a.blend', b'not opened'))
        self.assertIn('unsupported_binary_or_format_not_scanned', self.codes('a.mp3', b'not decoded'))

    def test_no_symlink_or_credential_store_reads(self):
        self.put('target.txt', b'clean')
        (self.root / 'link.txt').symlink_to('target.txt')
        self.put('.env', FAKE_TOKEN)
        self.put('.git/private.txt', FAKE_TOKEN)
        report = pf.audit(self.root)
        codes = {v['code'] for v in report['findings']}
        self.assertIn('credential_store_name_not_read', codes)
        self.assertIn('symlink_not_followed', codes)
        self.assertIn('excluded_directory_not_read', codes)
        self.assertNotIn('credential_like_pattern', codes)

    def test_output_redacts_sensitive_filename(self):
        name = FAKE_TOKEN.decode() + '.txt'
        self.put(name, FAKE_PATH)
        report = pf.audit(self.root)
        self.assertNotIn(name, json.dumps(report))
        self.assertTrue(report['findings'])
        self.assertTrue(report['findings'][0]['file'].startswith('[redacted-file-'))

    def test_tracked_only_and_no_mutation(self):
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        path = self.put('tracked.txt', b'clean')
        subprocess.run(['git', '-C', str(self.root), 'add', 'tracked.txt'], check=True)
        self.put('untracked.txt', FAKE_TOKEN)
        before = path.read_bytes()
        report = pf.audit(self.root, tracked=True)
        self.assertEqual(report['selected_paths'], 1)
        self.assertEqual(report['findings'], [])
        self.assertEqual(path.read_bytes(), before)

    def test_explicit_credential_directory_rejected(self):
        store = self.root / '.aws' / 'nested'
        store.mkdir(parents=True)
        with self.assertRaises(pf.Incomplete):
            pf.audit(store)

    def test_explicit_target_required(self):
        result = subprocess.run(['python3', str(Path(pf.__file__))], capture_output=True)
        self.assertEqual(result.returncode, 2)


if __name__ == '__main__':
    unittest.main()
