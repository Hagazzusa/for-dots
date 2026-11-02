"""Remove PNG ancillary metadata without decoding or altering pixel payloads."""
import struct
from pathlib import Path
root=Path(__file__).resolve().parent
for p in [root/'folded_path.png', *sorted((root/'frames').glob('*.png'))]:
    raw=p.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n';out=raw[:8];i=8
    while i<len(raw):
        n=struct.unpack('>I',raw[i:i+4])[0];kind=raw[i+4:i+8];chunk=raw[i:i+n+12]
        # Retain mandatory image chunks and explicit color profile information.
        if kind in [b'IHDR',b'IDAT',b'IEND',b'PLTE',b'tRNS',b'sRGB',b'gAMA',b'cHRM',b'iCCP']:out+=chunk
        i+=n+12
    p.write_bytes(out)
print('Removed ancillary textual/EXIF metadata without altering compressed pixel data.')
