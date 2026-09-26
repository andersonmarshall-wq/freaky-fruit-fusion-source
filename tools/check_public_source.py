#!/usr/bin/env python3
"""Reject tracked local asset files, archives, build outputs, and signing material."""
import fnmatch
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / "assets.local.json").read_text())
local_paths = {entry["path"] for entry in manifest["files"]}
local_hashes = {entry["sha256"] for entry in manifest["files"]}
patterns = ["art/kawaii/*.svg", "images/ball_*.png", "Kawaii_Fruit_Preview.png",
            "*.ttf", "*.zip", "*.apk", "*.aab", "*.keystore", "*.der", "*.pem",
            "*.p12", "*.key", "*.env", ".env", "build/*", ".internal/*"]
files = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).split(b"\0")
blocked = []
for raw in filter(None, files):
    name = raw.decode()
    path = ROOT / name
    if (name in local_paths or any(fnmatch.fnmatch(name, pattern) for pattern in patterns)
            or (path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() in local_hashes)):
        blocked.append(name)
if blocked:
    print("Do not publish these local-only files:\n" + "\n".join(blocked))
    sys.exit(1)
print(f"PASS: {len(list(filter(None, files)))} tracked files contain no listed local-only assets or build archives.")
