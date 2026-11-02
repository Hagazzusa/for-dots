#!/usr/bin/env python3
"""Local byte snapshot of an explicit allowlist. No network or metadata edits."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys

from check_public_assets import SENSITIVE_NAMES, SKIP_DIRS

MAX_LIST_BYTES = 1024 * 1024
MAX_FILES = 10000
BLOCKED = SKIP_DIRS | SENSITIVE_NAMES | {'.cache', 'node_modules', '.venv', 'venv', '.hg', '.svn'}


class SnapshotError(ValueError):
    """Messages intentionally omit user paths and file contents."""


def signature(st):
    return (st.st_dev, st.st_ino, st.st_mode, st.st_size, st.st_mtime_ns, st.st_ctime_ns)


def safe_name(name):
    if not isinstance(name, str) or not name or '\\' in name or ':' in name:
        raise SnapshotError('invalid_relative_path')
    parts = name.split('/')
    if any(not p or p in ('.', '..') or any(ord(c) < 32 for c in p) for p in parts):
        raise SnapshotError('noncanonical_relative_path')
    if PurePosixPath(name).is_absolute():
        raise SnapshotError('absolute_path')
    if any(p.lower() in BLOCKED or p.lower().startswith('.env.') for p in parts):
        raise SnapshotError('excluded_path')
    return name


def checked_path(path, directory=False):
    """Reject symlinks and excluded ancestors before opening selected data."""
    path = Path(os.path.abspath(path))
    for item in [*reversed(path.parents), path]:
        if item.name.lower() in BLOCKED or item.name.lower().startswith('.env.'):
            raise SnapshotError('excluded_ancestor')
        st = item.lstat()
        if stat.S_ISLNK(st.st_mode):
            raise SnapshotError('symlink_not_allowed')
        if item != path and not stat.S_ISDIR(st.st_mode):
            raise SnapshotError('non_directory_ancestor')
    if directory and not stat.S_ISDIR(st.st_mode):
        raise SnapshotError('directory_required')
    if not directory and not stat.S_ISREG(st.st_mode):
        raise SnapshotError('regular_file_required')
    return path, st


def read_file(path, expected, sink=None):
    path, current = checked_path(path)
    if signature(current) != expected:
        raise SnapshotError('source_changed_before_read')
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    fd = os.open(path, flags)
    with os.fdopen(fd, 'rb') as source:
        if signature(os.fstat(source.fileno())) != expected:
            raise SnapshotError('source_changed_on_open')
        sha256 = hashlib.sha256()
        blob = hashlib.sha1(b'blob ' + str(current.st_size).encode('ascii') + b'\0')
        remaining = current.st_size
        while remaining:
            chunk = source.read(min(1024 * 1024, remaining))
            if not chunk:
                raise SnapshotError('source_truncated')
            remaining -= len(chunk)
            sha256.update(chunk)
            blob.update(chunk)
            if sink is not None:
                sink.write(chunk)
        if source.read(1) or signature(os.fstat(source.fileno())) != expected:
            raise SnapshotError('source_changed_during_read')
    if signature(checked_path(path)[1]) != expected:
        raise SnapshotError('source_changed_after_read')
    return sha256.hexdigest(), blob.hexdigest()


def load_allowlist(path):
    path, st = checked_path(path)
    if st.st_size > MAX_LIST_BYTES:
        raise SnapshotError('allowlist_too_large')
    with path.open('rb') as stream:
        data = stream.read(MAX_LIST_BYTES + 1)
    if len(data) > MAX_LIST_BYTES or signature(checked_path(path)[1]) != signature(st):
        raise SnapshotError('allowlist_changed')
    names = json.loads(data)
    if not isinstance(names, list) or not 1 <= len(names) <= MAX_FILES:
        raise SnapshotError('allowlist_requires_nonempty_bounded_array')
    names = [safe_name(n) for n in names]
    # Portable case-folded aliases are conservatively rejected on every OS.
    folded = [n.casefold() for n in names]
    if len(set(folded)) != len(folded):
        raise SnapshotError('duplicate_path')
    selected = set(folded)
    if any('/'.join(n.split('/')[:i]) in selected for n in folded for i in range(1, len(n.split('/')))):
        raise SnapshotError('file_directory_conflict')
    return names


def freeze(source, allowlist, destination):
    source, _ = checked_path(source, directory=True)
    names = load_allowlist(allowlist)
    dest = Path(os.path.abspath(destination))
    checked_path(dest.parent, directory=True)
    safe_name(dest.name)
    if source == dest or source in dest.parents or dest in source.parents:
        raise SnapshotError('source_destination_overlap')
    if os.path.lexists(dest):
        raise SnapshotError('destination_exists')
    states = {name: signature(checked_path(source / name)[1]) for name in names}
    # Atomic reservation; a concurrent creator wins rather than being overwritten.
    dest.mkdir(mode=0o700)
    marker = dest / 'INCOMPLETE'
    with marker.open('xb') as f:
        f.write(b'Incomplete local snapshot. Do not publish or overwrite.\n')
    files = dest / 'files'
    files.mkdir()
    entries = []
    for name in names:
        target = files / name
        target.parent.mkdir(parents=True, exist_ok=True)
        checked_path(target.parent, directory=True)
        with target.open('xb') as out:
            digest, blob = read_file(source / name, states[name], out)
            out.flush()
            os.fsync(out.fileno())
        copied = signature(checked_path(target)[1])
        if read_file(target, copied) != (digest, blob):
            raise SnapshotError('copy_hash_mismatch')
        entries.append({'path': name, 'localpath': str(target), 'size': copied[3],
                        'sha256': digest, 'sha': blob})
    # Recheck every selected source after the last copy, not only per-file reads.
    for entry in entries:
        if read_file(source / entry['path'], states[entry['path']]) != (entry['sha256'], entry['sha']):
            raise SnapshotError('source_changed_during_snapshot')
        target = files / entry['path']
        if read_file(target, signature(checked_path(target)[1])) != (entry['sha256'], entry['sha']):
            raise SnapshotError('copy_changed_during_snapshot')
    report = {'format_version': 1, 'status': 'complete', 'scope': 'Internal local paths; not a public repository manifest or publication approval.',
              'file_count': len(entries), 'total_bytes': sum(e['size'] for e in entries), 'files': entries}
    with (dest / 'SNAPSHOT_MANIFEST.json').open('x', encoding='utf-8') as out:
        json.dump(report, out, ensure_ascii=False, indent=2)
        out.write('\n')
        out.flush()
        os.fsync(out.fileno())
    marker.unlink()
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--allowlist', required=True, help='JSON array of exact relative file paths')
    parser.add_argument('--destination', required=True, help='New directory, outside source; parent must exist')
    args = parser.parse_args()
    try:
        result = freeze(args.source, args.allowlist, args.destination)
    except (OSError, ValueError, TypeError):
        print('Snapshot failed; no existing destination was overwritten. Any new INCOMPLETE directory is preserved for inspection.', file=sys.stderr)
        return 1
    print(json.dumps({'status': 'complete', 'file_count': result['file_count'], 'total_bytes': result['total_bytes']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
