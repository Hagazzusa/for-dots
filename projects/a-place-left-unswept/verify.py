"""원본 PNG와 공개 프로젝트 파일을 변경하지 않고 검사한다."""
import hashlib
import json
from pathlib import Path
import struct
import zlib
from PIL import Image

ROOT = Path(__file__).resolve().parent
NAME = "output/A-Place-Left-Unswept.png"
with Image.open(ROOT / NAME) as im:
    im.load()
    assert im.format == "PNG" and im.size == (1536, 1024) and im.mode == "RGB"
raw = (ROOT / NAME).read_bytes()
assert raw[:8] == bytes.fromhex("89504e470d0a1a0a")
pos = 8
chunks = []
while pos < len(raw):
    assert pos + 12 <= len(raw)
    size = struct.unpack(">I", raw[pos:pos+4])[0]
    end = pos + 12 + size
    assert end <= len(raw)
    tag = raw[pos+4:pos+8]
    data = raw[pos+8:pos+8+size]
    crc = struct.unpack(">I", raw[pos+8+size:end])[0]
    assert zlib.crc32(tag + data) & 0xffffffff == crc
    chunks.append(tag.decode("ascii"))
    pos = end
assert chunks[0] == "IHDR" and chunks[-1] == "IEND"
manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
assert manifest["algorithm"] == "sha256"
seen = set()
for row in manifest["files"]:
    name = row["path"]
    rel = Path(name)
    assert not rel.is_absolute() and ".." not in rel.parts and name not in seen
    seen.add(name)
    p = ROOT / rel
    assert not p.is_symlink()
    data = p.read_bytes()
    assert len(data) == row["bytes"] and hashlib.sha256(data).hexdigest() == row["sha256"], name
assert {NAME, "prompt.txt", "README.md", "verify.py", "qa.json"}.issubset(seen)
print("PNG 전체 디코드·크기·RGB·청크 CRC와", len(seen), "개 파일 해시: 통과")
