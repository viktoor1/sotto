#!/usr/bin/env python3
"""Package this issue's review evidence; include no surrounding workspace files."""
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parent
target = root.parent / "sotto-637-shareable.zip"
manifest_path = root / "shareable-bundle-manifest.json"
files = sorted(p for p in root.rglob("*") if p.is_file()
               and p != manifest_path and "__pycache__" not in p.parts)
assert all(not p.is_symlink() for p in files)
assert all(p.suffix.lower() in {".md", ".html", ".in", ".py", ".js", ".css", ".mjs",
                               ".json", ".jsonl", ".log", ".png", ".patch", ".tsx", ".txt"}
           for p in files), "Unexpected file type needs review before sharing"
manifest = {"createdAt": datetime.now(timezone.utc).isoformat(),
            "scope": "Sotto #637 task folder only; no desktop screenshots, credentials or surrounding workspace",
            "activityRecordCount": len((root / "activity.jsonl").read_text().splitlines()),
            "files": {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
files.append(manifest_path)
with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in files:
        archive.write(path, "sotto-637-evidence/" + str(path.relative_to(root)))
with zipfile.ZipFile(target) as archive:
    assert archive.testzip() is None
    assert len(archive.namelist()) == len(files)
    for path in files:
        assert archive.read("sotto-637-evidence/" + str(path.relative_to(root))) == path.read_bytes()
print("Verified shareable archive:", target)
print("Files:", len(files), "bytes:", target.stat().st_size)
print("Activity records captured:", manifest["activityRecordCount"])
print("Archive SHA256:", hashlib.sha256(target.read_bytes()).hexdigest())
