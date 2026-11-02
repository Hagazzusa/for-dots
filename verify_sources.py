"""Offline checkpoint integrity; --refresh explicitly inventories Git-tracked files."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / 'SOURCE_MANIFEST.json'


def safe_file(name):
    parts = PurePosixPath(name)
    if (not name or '\\' in name or ':' in name or parts.is_absolute()
            or any(p in ('', '..', '.') for p in name.split('/'))):
        raise ValueError('Unsafe manifest path: ' + name)
    path = ROOT
    for part in parts.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError('Symlink is not supported: ' + name)
    if not path.is_file():
        raise ValueError('Missing regular file: ' + name)
    return path


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true', help='Replace manifest from reviewed Git-tracked working files')
    args = parser.parse_args()
    if MANIFEST.is_symlink():
        raise ValueError('Manifest symlinks are not supported')
    if args.refresh:
        names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode('utf-8').split('\0')
        rows = []
        for name in sorted(set(names) - {'', MANIFEST.name}):
            path = safe_file(name)
            rows.append({'path': name, 'size': path.stat().st_size, 'sha256': digest(path)})
        MANIFEST.write_text(json.dumps({'format': 1, 'algorithm': 'sha256', 'files': rows}, indent=2) + '\n', encoding='utf-8')
        print('Refreshed {} files; review the manifest diff.'.format(len(rows)))
        return 0
    data = json.loads(MANIFEST.read_text(encoding='utf-8'))
    if data.get('format') != 1 or data.get('algorithm') != 'sha256':
        raise ValueError('Unsupported manifest format')
    rows = data['files']
    if not rows:
        raise ValueError('Empty manifest')
    seen, failures = set(), []
    for row in rows:
        name = row['path']
        if name in seen or name == MANIFEST.name:
            raise ValueError('Duplicate or self-referencing manifest entry: ' + name)
        seen.add(name)
        try:
            path = safe_file(name)
            if path.stat().st_size != row['size'] or digest(path) != row['sha256']:
                failures.append('Changed: ' + name)
        except ValueError as exc:
            failures.append(str(exc))
    if failures:
        print('\n'.join(failures), file=sys.stderr)
        return 1
    print('Verified {} files ({} bytes). Unlisted files are ignored.'.format(len(rows), sum(r['size'] for r in rows)))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(run())
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print('Verification error: ' + str(exc), file=sys.stderr)
        sys.exit(1)
