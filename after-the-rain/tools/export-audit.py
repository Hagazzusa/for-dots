#!/usr/bin/env python3
"""Build a main-scene PCK without export templates, then audit it in isolation.

Usage: python3 tools/export-audit.py [--output /outside/project/game.pck]
First run tools/run_checks.sh (or --fresh-import). Uses its same serial engine lock.
GODOT_BIN, RAIN_QA_ROOT and RAIN_TEST_TIMEOUT may override defaults. No publishing.
"""
from __future__ import annotations
import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
ERRORS = re.compile(r'SCRIPT ERROR|(?:^|\s)ERROR:|QA FAIL|(?:^|\s)FAIL:|instances leaked|resources still in use', re.M)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='External destination; default is inside sibling qa_work.')
    args = parser.parse_args()
    work = Path(os.environ.get('RAIN_QA_ROOT', ROOT.parent / 'qa_work')).expanduser().resolve()
    if work == ROOT or ROOT in work.parents:
        parser.error('RAIN_QA_ROOT must be outside the source project.')
    work.mkdir(parents=True, exist_ok=True)
    with (work / 'engine.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print('Another check/export owns the serial engine slot.')
            return 3
        for name in ('tmp', 'data', 'config', 'cache', 'logs'):
            (work / name).mkdir(exist_ok=True)
        env = os.environ.copy()
        env.update(TMPDIR=str(work / 'tmp'), XDG_DATA_HOME=str(work / 'data'),
                   XDG_CONFIG_HOME=str(work / 'config'), XDG_CACHE_HOME=str(work / 'cache'))
        engine = os.environ.get('GODOT_BIN', 'godot')
        timeout = float(os.environ.get('RAIN_TEST_TIMEOUT', '120'))
        run = Path(tempfile.mkdtemp(prefix=time.strftime('export-%Y%m%dT%H%M%S-'), dir=work / 'logs'))
        isolated = run / 'isolated'
        isolated.mkdir()
        pack = isolated / 'production.pck'
        helper = run / 'external-pack-check.gd'
        shutil.copyfile(ROOT / 'tools/export-pack-check.gd', helper)

        def execute(label: str, command: list[str], cwd: Path) -> bool:
            logfile = run / f'{label}.log'
            try:
                with logfile.open('w') as stream:
                    result = subprocess.run(command, cwd=cwd, env=env, stdout=stream,
                                            stderr=subprocess.STDOUT, timeout=timeout, check=False)
                text = logfile.read_text(errors='replace')
                okay = result.returncode == 0 and ERRORS.search(text) is None
            except (OSError, subprocess.TimeoutExpired) as exc:
                with logfile.open('a') as stream:
                    stream.write(f'\nERROR: {exc}\n')
                okay = False
            print(f'{"PASS" if okay else "FAIL"} {label}: {logfile}')
            if not okay:
                print('\n'.join(logfile.read_text(errors='replace').splitlines()[-25:]))
            return okay

        if not execute('build', [engine, '--headless', '--path', str(ROOT), '--script',
                                str(helper), '--', '--build-pck', str(pack)], ROOT):
            return 1
        manifest = Path(str(pack) + '.manifest.json')
        if not pack.is_file() or not manifest.is_file():
            print('FAIL: Build did not produce both PCK and manifest.')
            return 1
        entries = json.loads(manifest.read_text())
        required = {'res://project.godot', 'res://main.tscn', 'res://scripts/session.gd',
                    'res://config/rain_positions.json'}
        if not required.issubset(entries):
            print('FAIL: Manifest lacks expected core runtime files.')
            return 1
        # The helper lives outside both project and pack. Physical res:// here has
        # no source files, so missing packed dependencies cannot fall back to source.
        command = [engine, '--headless', '--path', str(isolated), '--main-pack', str(pack),
                   '--script', str(helper), '--', '--audit-pck', str(manifest)]
        normal = execute('packed-normal', command, isolated)
        test_arg = execute('packed-test-flag', command + ['--test'], isolated)
        if not (normal and test_arg):
            return 1
        if args.output:
            output = args.output.expanduser().resolve()
            if output == ROOT or ROOT in output.parents:
                parser.error('--output must be outside the source project.')
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(pack, output)
            shutil.copyfile(manifest, Path(str(output) + '.manifest.json'))
            print(f'Validated PCK copied to {output}')
        else:
            print(f'Validated PCK: {pack}')
        print(f'EXPORT AUDIT PASS: {len(entries)} files; isolated normal/--test input enabled; no fixtures. Logs: {run}')
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
