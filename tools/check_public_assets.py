#!/usr/bin/env python3
"""Read-only metadata preflight. Findings require review, never publication approval."""
import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
import zlib

MAX_METADATA = 1024 * 1024
MAX_TEXT = 4 * MAX_METADATA
MAX_FILES = 10000
TEXT_EXT = {'.py', '.gd', '.tscn', '.tres', '.godot', '.md', '.txt', '.json', '.csv', '.svg', '.xml', '.toml', '.yaml', '.yml', '.ini', '.cfg', '.sh'}
PRIVATE = re.compile(rb'(?<![A-Za-z0-9:/])(?:/' + b'workspace/|/' + rb'home/[^/\s]+/|/' + rb'Users/[^/\s]+/|[A-Za-z]:[\\/]Users[\\/][^\\/\s]+[\\/])', re.I)
TOKEN = re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16})\b|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
ABSOLUTE_METADATA = re.compile(rb'(?<![A-Za-z0-9:/])(?:/(?:tmp|var|opt|mnt|workspace|home|Users)/[^\s\x00]+|[A-Za-z]:[\\/][^\s\x00]+)')
SENSITIVE_NAMES = {'.netrc', '.git-credentials', '.npmrc', '.pypirc', 'auth.json', 'tokens.json', '.env', 'credentials', 'credentials.json', 'hosts.yml', 'id_rsa', 'id_ed25519'}
SKIP_DIRS = {'.git', '.godot', '__pycache__', '.ssh', '.aws', '.config', '.codex'}


class Incomplete(ValueError):
    pass


def bounded_inflate(data):
    dec = zlib.decompressobj()
    out = dec.decompress(data, MAX_METADATA + 1)
    if len(out) > MAX_METADATA or dec.unconsumed_tail or not dec.eof:
        raise Incomplete('compressed_metadata_limit_or_invalid_stream')
    return out


def text_patterns(data, metadata=False):
    kinds = []
    if PRIVATE.search(data):
        kinds.append('private_absolute_path_pattern')
    if TOKEN.search(data):
        kinds.append('credential_like_pattern')
    if metadata and ABSOLUTE_METADATA.search(data) and 'private_absolute_path_pattern' not in kinds:
        kinds.append('absolute_metadata_path')
    return kinds


def png_metadata(path):
    result, total, decoded_total, chunks = [], 0, 0, 0
    size = path.stat().st_size
    with path.open('rb') as f:
        if f.read(8) != b'\x89PNG\r\n\x1a\n':
            raise Incomplete('invalid_png_signature')
        while f.tell() < size:
            head = f.read(8)
            if len(head) != 8:
                raise Incomplete('truncated_png_chunk')
            n, kind = struct.unpack('>I4s', head)
            chunks += 1
            if chunks > 100000 or n + 4 > size - f.tell():
                raise Incomplete('png_chunk_limit_or_truncation')
            if kind in (b'tEXt', b'zTXt', b'iTXt', b'eXIf'):
                total += n
                if total > MAX_METADATA:
                    raise Incomplete('png_metadata_size_limit')
                raw = f.read(n)
                crc = f.read(4)
                if struct.unpack('>I', crc)[0] != zlib.crc32(kind + raw) & 0xffffffff:
                    raise Incomplete('png_metadata_crc_error')
                if kind == b'tEXt':
                    if b'\0' not in raw:
                        raise Incomplete('invalid_png_text')
                    text = raw
                elif kind == b'zTXt':
                    key, rest = raw.split(b'\0', 1)
                    if not rest or rest[0] != 0:
                        raise Incomplete('invalid_png_compression')
                    text = key + b'\0' + bounded_inflate(rest[1:])
                elif kind == b'iTXt':
                    key, rest = raw.split(b'\0', 1)
                    flag, method = rest[:2]
                    if flag not in (0, 1) or method != 0:
                        raise Incomplete('invalid_png_international_text')
                    lang, translated, text = rest[2:].split(b'\0', 2)
                    text = key + b'\0' + lang + b'\0' + translated + b'\0' + (bounded_inflate(text) if flag else text)
                else:
                    # Raw pattern scan is incomplete for structured/encoded EXIF.
                    text = raw
                    result.append(('manual', 'png_exif_requires_structured_review'))
                decoded_total += len(text)
                if decoded_total > MAX_METADATA:
                    raise Incomplete('png_decoded_metadata_size_limit')
                result.extend(('finding', k) for k in text_patterns(text, True))
            else:
                f.seek(n + 4, 1)  # Never decode image pixels.
            if kind == b'IEND':
                if n != 0 or f.tell() != size:
                    raise Incomplete('invalid_png_termination')
                return result
        raise Incomplete('missing_png_termination')


def exr_metadata(path):
    result = []
    with path.open('rb') as f:
        head = f.read(8)
        if len(head) != 8 or head[:4] != b'v/1\x01':
            raise Incomplete('invalid_exr_signature')
        version = struct.unpack('<I', head[4:])[0]
        if version & 0xff != 2 or version & (0x800 | 0x1000):
            raise Incomplete('deep_or_multipart_exr_requires_native_review')
        def cstring():
            value = bytearray()
            while len(value) <= 255 and f.tell() <= MAX_METADATA:
                b = f.read(1)
                if not b:
                    raise Incomplete('truncated_exr_header')
                if b == b'\0':
                    return bytes(value)
                value.extend(b)
            raise Incomplete('exr_header_limit')
        while True:
            name = cstring()
            if not name:
                return result
            kind = cstring()
            rawsize = f.read(4)
            if len(rawsize) != 4:
                raise Incomplete('truncated_exr_attribute')
            n = struct.unpack('<I', rawsize)[0]
            if n > MAX_METADATA or f.tell() + n > MAX_METADATA:
                raise Incomplete('exr_header_limit')
            data = f.read(n)
            if len(data) != n:
                raise Incomplete('truncated_exr_attribute')
            if kind in (b'string', b'stringvector'):
                result.extend(('finding', k) for k in text_patterns(data, True))
                # Any absolute File value, including unusual root directories.
                if name.lower() == b'file' and (data.startswith(b'/') or re.match(rb'^[A-Za-z]:[\\/]', data)):
                    result.append(('finding', 'absolute_exr_file_attribute'))


def cad_metadata(path):
    result, total = [], 0
    # Bound the central directory before ZipFile constructs its member list.
    with path.open('rb') as stream:
        size = path.stat().st_size
        stream.seek(max(0, size - 65577))
        tail = stream.read(65577)
    pos = tail.rfind(b'PK\x05\x06')
    if pos < 0 or pos + 22 > len(tail):
        raise Incomplete('cad_zip_directory_missing')
    if pos >= 20 and tail[pos - 20:pos - 16] == b'PK\x06\x07':
        raise Incomplete('zip64_requires_native_review')
    if b'PK\x06\x06' in tail[:pos]:
        raise Incomplete('zip64_requires_native_review')
    disk, start_disk, disk_entries, entries, central_size, offset, comment = struct.unpack('<4H2IH', tail[pos + 4:pos + 22])
    if (disk or start_disk or entries != disk_entries or entries > 512
            or central_size > MAX_METADATA or offset + central_size > size
            or pos + 22 + comment != len(tail)):
        raise Incomplete('cad_zip_directory_limit_or_unsupported')
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        if len(entries) > 512:
            raise Incomplete('cad_member_count_limit')
        for entry in entries:
            name = PurePosixPath(entry.filename)
            if name.is_absolute() or '..' in name.parts or '\\' in entry.filename or ':' in entry.filename:
                result.append(('finding', 'unsafe_cad_member_name'))
            if not entry.filename.lower().endswith('.xml'):
                continue
            total += entry.file_size
            if entry.flag_bits & 1 or entry.file_size > MAX_METADATA or total > MAX_TEXT:
                raise Incomplete('cad_xml_encrypted_or_size_limit')
            with archive.open(entry) as stream:
                data = stream.read(MAX_METADATA + 1)
            if len(data) > MAX_METADATA:
                raise Incomplete('cad_xml_size_limit')
            result.extend(('finding', k) for k in text_patterns(data, True))
            declaration_probe = data.replace(b'\0', b'').upper()
            if b'<!DOCTYPE' in declaration_probe or b'<!ENTITY' in declaration_probe:
                result.append(('manual', 'xml_declarations_not_parsed'))
            else:
                node = ET.fromstring(data)
                values = []
                for element in node.iter():
                    values.extend(element.attrib.values())
                    values.extend(v for v in (element.text, element.tail) if v)
                decoded = '\n'.join(values).encode('utf-8')
                result.extend(('finding', k) for k in text_patterns(decoded, True))
        result.append(('manual', 'cad_binary_geometry_and_properties_need_native_review'))
    return result


def inspect_file(path):
    suffix = path.suffix.lower()
    if path.name in SENSITIVE_NAMES or path.name.startswith('.env.'):
        return [('manual', 'credential_store_name_not_read')]
    try:
        if suffix == '.blend':
            return [('manual', 'blend_requires_native_read_only_audit')]
        if suffix == '.png':
            return png_metadata(path)
        if suffix == '.exr':
            return exr_metadata(path)
        if suffix == '.fcstd':
            return cad_metadata(path)
        if suffix in TEXT_EXT or path.name == '.gitignore':
            if path.stat().st_size > MAX_TEXT:
                return [('manual', 'text_size_limit')]
            data = path.read_bytes()
            data.decode('utf-8')
            return [('finding', k) for k in text_patterns(data)]
        return [('manual', 'unsupported_binary_or_format_not_scanned')]
    except (OSError, ValueError, struct.error, zlib.error, zipfile.BadZipFile, ET.ParseError, NotImplementedError, RuntimeError):
        # Exceptions can contain private path/metadata values: never echo them.
        return [('manual', 'metadata_incomplete_invalid_or_limit_reached')]


def select_paths(root, tracked):
    if tracked:
        raw = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', '-C', str(root), 'ls-files', '-z'], stderr=subprocess.DEVNULL)
        return [Path(n) for n in raw.decode('utf-8').split('\0') if n]
    names = []
    def unavailable(_error):
        raise Incomplete('directory_walk_unavailable')
    for base, dirs, files in os.walk(root, followlinks=False, onerror=unavailable):
        # Report excluded directories, but never open their contents.
        for name in sorted(list(dirs)):
            path = Path(base) / name
            if name in SKIP_DIRS or path.is_symlink():
                names.append(path.relative_to(root))
                dirs.remove(name)
        names.extend((Path(base) / name).relative_to(root) for name in files)
        if len(names) > MAX_FILES:
            raise Incomplete('target_file_count_limit')
    return names


def audit(root, tracked=False):
    root = Path(root).absolute()
    if any(p.name in {'.ssh', '.aws', '.config', '.codex'} for p in [root, *root.parents]):
        raise Incomplete('credential_or_config_directory_not_read')
    if any(p.is_symlink() for p in [root, *root.parents]) or not root.is_dir():
        raise Incomplete('target_must_be_real_directory')
    names = select_paths(root, tracked)
    if len(names) > MAX_FILES:
        raise Incomplete('target_file_count_limit')
    findings = []
    for number, rel in enumerate(sorted(set(names)), 1):
        name = rel.as_posix()
        # Filenames can themselves carry sensitive values: redact if matched.
        label = '[redacted-file-{}]'.format(number) if text_patterns(name.encode()) else name
        parts = PurePosixPath(name).parts
        if rel.is_absolute() or '..' in parts or ':' in name or '\\' in name:
            checks = [('manual', 'unsafe_target_path_not_read')]
            label = '[redacted-file-{}]'.format(number)
        elif any(part in SKIP_DIRS for part in parts):
            checks = [('manual', 'excluded_directory_not_read')]
        elif any((root.joinpath(*parts[:i])).is_symlink() for i in range(1, len(parts) + 1)):
            checks = [('manual', 'symlink_not_followed')]
        elif not (root / rel).is_file():
            checks = [('manual', 'missing_or_nonregular_file')]
        else:
            checks = inspect_file(root / rel)
        for level, code in sorted(set(checks)):
            findings.append({'file': label, 'level': level, 'code': code})
    return {'scope': 'Read-only bounded metadata patterns; not security certification or publication permission.',
            'selected_paths': len(names), 'findings': findings,
            'status': 'review_required' if findings else 'no_target_patterns_found',
            'limitations': ['No semantic privacy inference or authorship/license verification.',
                            'No native Blender audit, binary geometry inspection, audio/video metadata decoding or image-pixel decoding.',
                            'No assurance against concurrent file mutation; run on a frozen trusted staging copy.',
                            'No autofix, deletion, upload, credential-store access or network requests.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--directory', type=Path, help='Explicit asset directory, recursive without symlinks')
    group.add_argument('--tracked', type=Path, help='Explicit Git worktree; tracked files only')
    args = parser.parse_args()
    try:
        report = audit(args.directory or args.tracked, args.tracked is not None)
    except (OSError, ValueError, subprocess.CalledProcessError, UnicodeError):
        print(json.dumps({'status': 'incomplete', 'code': 'target_unavailable_invalid_or_limit_reached'}))
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=True))
    return 1 if report['findings'] else 0


if __name__ == '__main__':
    sys.exit(main())
