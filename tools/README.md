# Publication preflight helpers

`check_public_assets.py` is a **read-only, standard-library metadata-pattern check** for a deliberately selected staging directory. It is not a security certification, a full secret detector, a privacy-context interpreter, a license check, or permission to publish.

```sh
python3 tools/check_public_assets.py --directory garden-of-light
# Or select only tracked files of an explicit Git worktree:
python3 tools/check_public_assets.py --tracked .
python3 tools/test_check_public_assets.py
```

Python 3.8+; Git is needed only for `--tracked`. No engines, plugins, network services or credentials are used. Run against a frozen trusted staging copy, not a live credential directory. Directory traversal does not follow symlinks. Known credential-store names and development/config directories are reported without reading their contents. There is no automatic upload, edit, deletion or sanitization.

## What it checks

- Selected UTF-8 text files: common private absolute-path patterns and a limited set of credential-like prefixes/private-key markers. Ordinary source identifiers such as `password` or `api_token = None` are not credentials.
- PNG: `tEXt`, compressed `zTXt`, and `iTXt` metadata, bounded decompression and metadata CRCs. EXIF gets a raw pattern scan **and requires structured manual review**, even when it is only benign resolution data. No pixels are decoded.
- OpenEXR: bounded string attributes, especially absolute `File` paths. Deep/multipart files require native review. Channel/pixel data is not decoded or altered.
- FreeCAD `.FCStd`: bounded ZIP central directory and XML metadata, including decoded XML values. No archive extraction; ZIP64 is conservatively unsupported. Native binary geometry/properties still require review. Entity declarations are not expanded.
- `.blend`: always **manual native read-only audit required**, including compressed files. The script never treats a raw string scan as sufficient Blender inspection.
- Audio, video and other unsupported formats: explicitly unscanned/manual, not implicitly clean.

Limits: 10,000 selected paths; 4 MiB per text file; 1 MiB PNG encoded/decoded metadata or EXR header; 512 CAD members, 1 MiB ZIP central directory/per-XML data and 4 MiB total XML. Oversize, malformed or unavailable data is **incomplete/manual**, never a clean result. Some real assets legitimately exceed these limits. These bounds apply to selected metadata, not total runtime or initial directory/Git enumeration: listing a huge worktree can allocate before the path-count limit is checked. Use a bounded, trusted staging directory; this is not an adversarial filesystem sandbox.

## Output and follow-up

JSON findings contain relative file locations and fixed reason codes, never matched values or exception text. Suspicious filenames are redacted. This does not hide ordinary relative names, and no output should be blindly published without review.

Exit codes:
- `0`: no targeted patterns found in inspected portions; **not publication clearance**.
- `1`: finding or manual-review item exists (including intentionally unsupported files).
- `2`: explicit target could not be selected or completed.

Review every finding and inspect unsupported/native formats separately. Absolute-path flags can be intentional public code examples; credential-like matches can be synthetic fixtures. Conversely, unrecognized credentials, encoded text and private meaning may evade these finite patterns. There is no suppression/automatic-approval mechanism. Concurrent file replacement is outside this small utility's threat model; use frozen staging inputs.

The root `verify_sources.py` separately verifies exact checkpoint bytes. Do not confuse integrity hashes with metadata/privacy review. The synthetic unit suite tests redaction, clean encoder/source cases, compressed PNG metadata and limits, EXR paths, bounded CAD XML, symlink/store exclusions and tracked-only selection without real secrets.
