#!/usr/bin/env python3
"""Synthetic local-only tests; never opens real credentials or user assets."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import freeze_allowlist as snap


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.source = self.base / 'source'
        self.source.mkdir()
        (self.source / 'a.txt').write_bytes(b'original\x00bytes')
        self.allow = self.base / 'allow.json'
        self.dest = self.base / 'output'
        self.select(['a.txt'])

    def select(self, names):
        self.allow.write_text(json.dumps(names))

    def run_copy(self):
        return snap.freeze(self.source, self.allow, self.dest)

    def test_bytes_hashes_and_source_preserved(self):
        original = (self.source / 'a.txt').read_bytes()
        report = self.run_copy()
        entry = report['files'][0]
        self.assertEqual(Path(entry['localpath']).read_bytes(), original)
        self.assertEqual(entry['sha256'], hashlib.sha256(original).hexdigest())
        self.assertEqual(entry['sha'], hashlib.sha1(b'blob 14\0' + original).hexdigest())
        self.assertEqual(entry['size'], len(original))
        self.assertEqual((self.source / 'a.txt').read_bytes(), original)
        self.assertFalse((self.dest / 'INCOMPLETE').exists())
        self.assertEqual(json.loads((self.dest / 'SNAPSHOT_MANIFEST.json').read_text()), report)

    def test_empty_file_and_nested_unicode(self):
        (self.source / 'nested').mkdir()
        (self.source / 'nested/빈 파일').write_bytes(b'')
        self.select(['nested/빈 파일'])
        self.assertEqual(self.run_copy()['total_bytes'], 0)

    def test_paths_rejected(self):
        for name in ['../a.txt', '/a.txt', 'D:/a', 'a\\b', './a.txt', 'a//b', 'a/../b', '', 'a\n.txt']:
            with self.subTest(name=name):
                self.select([name])
                with self.assertRaises(snap.SnapshotError): self.run_copy()
                self.assertFalse(self.dest.exists())

    def test_excluded_names(self):
        for name in ['.git/config', '.godot/cache', '__pycache__/x', '.ssh/key', '.env', '.env.test', 'node_modules/x', 'credentials.json']:
            with self.subTest(name=name):
                self.select([name])
                with self.assertRaises(snap.SnapshotError): self.run_copy()
                self.assertFalse(self.dest.exists())

    def test_duplicate_and_portable_case_alias(self):
        for names in [['a.txt', 'a.txt'], ['a.txt', 'A.txt'], ['x', 'x/a']]:
            self.select(names)
            with self.assertRaises(snap.SnapshotError): self.run_copy()

    def test_bad_allowlist(self):
        for names in [[], {}, [3], ['a.txt'] * (snap.MAX_FILES + 1)]:
            self.select(names)
            with self.assertRaises(snap.SnapshotError): self.run_copy()

    def test_allowlist_limit(self):
        self.allow.write_bytes(b' ' * (snap.MAX_LIST_BYTES + 1))
        with self.assertRaises(snap.SnapshotError): self.run_copy()

    def test_missing_file_preflight(self):
        self.select(['missing'])
        with self.assertRaises(OSError): self.run_copy()
        self.assertFalse(self.dest.exists())

    def test_directory_not_file(self):
        (self.source / 'folder').mkdir(); self.select(['folder'])
        with self.assertRaises(snap.SnapshotError): self.run_copy()

    def test_file_symlink(self):
        (self.source / 'link').symlink_to(self.source / 'a.txt'); self.select(['link'])
        with self.assertRaises(snap.SnapshotError): self.run_copy()

    def test_ancestor_symlink(self):
        (self.source / 'link').symlink_to(self.source, target_is_directory=True); self.select(['link/a.txt'])
        with self.assertRaises(snap.SnapshotError): self.run_copy()

    def test_root_symlink(self):
        alias = self.base / 'alias'; alias.symlink_to(self.source, target_is_directory=True)
        with self.assertRaises(snap.SnapshotError): snap.freeze(alias, self.allow, self.dest)

    def test_allowlist_symlink(self):
        alias = self.base / 'list'; alias.symlink_to(self.allow)
        with self.assertRaises(snap.SnapshotError): snap.freeze(self.source, alias, self.dest)

    def test_output_parent_symlink(self):
        alias = self.base / 'alias'; alias.symlink_to(self.base, target_is_directory=True)
        with self.assertRaises(snap.SnapshotError): snap.freeze(self.source, self.allow, alias / 'out')

    def test_forbidden_root_ancestor(self):
        bad = self.base / '.config'; bad.mkdir()
        with self.assertRaises(snap.SnapshotError): snap.freeze(bad, self.allow, self.dest)

    def test_output_overlap(self):
        with self.assertRaises(snap.SnapshotError): snap.freeze(self.source, self.allow, self.source / 'out')

    def test_existing_destination_and_repeat_preserve(self):
        self.run_copy()
        first = (self.dest / 'SNAPSHOT_MANIFEST.json').read_bytes()
        with self.assertRaises(snap.SnapshotError): self.run_copy()
        self.assertEqual((self.dest / 'SNAPSHOT_MANIFEST.json').read_bytes(), first)

    def test_existing_empty_file_and_symlink_destinations(self):
        for kind in ['directory', 'file', 'symlink']:
            dest = self.base / kind
            if kind == 'directory': dest.mkdir()
            elif kind == 'file': dest.write_bytes(b'keep')
            else: dest.symlink_to(self.source)
            with self.assertRaises(snap.SnapshotError): snap.freeze(self.source, self.allow, dest)
            self.assertTrue(dest.exists())

    def test_partial_failure_preserved_and_not_retried_over(self):
        original = snap.read_file
        def fail(path, expected, sink=None):
            if sink is not None:
                sink.write(b'partial')
                raise OSError('synthetic write failure')
            return original(path, expected, sink)
        with patch.object(snap, 'read_file', fail):
            with self.assertRaises(OSError): self.run_copy()
        self.assertTrue((self.dest / 'INCOMPLETE').exists())
        self.assertFalse((self.dest / 'SNAPSHOT_MANIFEST.json').exists())
        self.assertEqual((self.dest / 'files/a.txt').read_bytes(), b'partial')
        with self.assertRaises(snap.SnapshotError): self.run_copy()
        self.assertEqual((self.source / 'a.txt').read_bytes(), b'original\x00bytes')

    def test_marker_creation_failure_never_means_success(self):
        original = Path.open
        def fail(path, *args, **kwargs):
            if path.name == 'INCOMPLETE': raise OSError('synthetic marker failure')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'open', fail):
            with self.assertRaises(OSError): self.run_copy()
        self.assertTrue(self.dest.is_dir())
        self.assertFalse((self.dest / 'SNAPSHOT_MANIFEST.json').exists())
        with self.assertRaises(snap.SnapshotError): self.run_copy()

    def test_source_change_during_stream_detected(self):
        path = self.source / 'a.txt'
        expected = snap.signature(path.stat())
        class MutatingSink:
            def write(self, chunk): path.write_bytes(b'altered source')
        with self.assertRaises(snap.SnapshotError):
            snap.read_file(path, expected, MutatingSink())

    def test_source_change_after_copy_detected(self):
        original = snap.read_file
        def change(path, expected, sink=None):
            result = original(path, expected, sink)
            if sink is not None: (self.source / 'a.txt').write_bytes(b'changed')
            return result
        with patch.object(snap, 'read_file', change):
            with self.assertRaises(snap.SnapshotError): self.run_copy()
        self.assertTrue((self.dest / 'INCOMPLETE').exists())

    def test_source_change_before_open_detected(self):
        p = self.source / 'a.txt'; sig = snap.signature(p.stat()); p.write_bytes(b'other')
        with self.assertRaises(snap.SnapshotError): snap.read_file(p, sig)

    def test_output_corruption_detected(self):
        original = snap.read_file
        def corrupt(path, expected, sink=None):
            result = original(path, expected, sink)
            if sink is not None:
                sink.flush()
                (self.dest / 'files/a.txt').write_bytes(b'corrupt')
            return result
        with patch.object(snap, 'read_file', corrupt):
            with self.assertRaises(snap.SnapshotError): self.run_copy()
        self.assertTrue((self.dest / 'INCOMPLETE').exists())


if __name__ == '__main__': unittest.main()
