#!/usr/bin/env python3
"""Restore locally licensed assets without adding them to public source control."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "assets.local.json").read_text())
FRUITS = ["Cherry", "Blueberry", "PassionFruit", "Kiwi", "Orange", "Peach",
          "Coconut", "Pineapple", "WatermelonFull"]
SFX = ["01_Soft_Bubble_Pop_v2.wav", "04_Jelly_Blob_Tap_v1.wav",
       "14_Star_Twinkle_v1.wav", "11_Magical_Sparkle_v2.wav",
       "08_Water_Droplet_Pop_v3.wav", "10_Marshmallow_Squish_v2.wav"]


def read_named(pack, name):
    """Read only an expected file; never extract arbitrary ZIP paths."""
    if pack.is_dir():
        matches = list(pack.rglob(name))
        if len(matches) != 1:
            raise ValueError(f"Expected one {name} in {pack}, found {len(matches)}")
        return matches[0].read_bytes()
    with zipfile.ZipFile(pack) as archive:
        matches = [n for n in archive.namelist()
                   if Path(n).name == name and "__MACOSX" not in Path(n).parts]
        if len(matches) != 1:
            raise ValueError(f"Expected one {name} in {pack}, found {len(matches)}")
        return archive.read(matches[0])


def run(script, *args):
    subprocess.run([sys.executable, str(ROOT / "tools" / script), *map(str, args)],
                   cwd=ROOT, check=True)


def restore_build(source):
    source = source.resolve()
    if source == ROOT:
        raise ValueError("Choose a separate complete build as the source")
    # Validate the complete input before writing anything.
    data = []
    for entry in MANIFEST["files"]:
        content = (source / entry["path"]).read_bytes()
        if hashlib.sha256(content).hexdigest() != entry["sha256"]:
            raise ValueError(f"Asset differs from the 0.2.1 snapshot: {entry['path']}")
        data.append((entry["path"], content))
    for name, content in data:
        target = ROOT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    print(f"Restored {len(data)} local asset files from the complete 0.2.1 build.")


def check():
    missing = [entry["path"] for entry in MANIFEST["files"]
               if entry["required_for_build"] and
               not ((ROOT / entry["path"]).is_file() and
                    (ROOT / entry["path"]).stat().st_size > 0)]
    if missing:
        print("Local assets still needed (see ASSETS.md):")
        print("\n".join("  " + name for name in missing))
        return 1
    print("All local assets required by the game are present.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-build", type=Path,
                        help="Your own complete licensed 0.2.1 project directory")
    parser.add_argument("--fruit-pack", type=Path,
                        help="Your purchased ItchIO_File.zip or extracted directory")
    parser.add_argument("--sfx-pack", type=Path,
                        help="Your Tiny Pops & Sparkles ZIP or extracted directory")
    parser.add_argument("--font", type=Path, help="Locally downloaded Mouldy Cheese TTF")
    parser.add_argument("--check", action="store_true", help="Check required local assets")
    args = parser.parse_args()
    if args.from_build and any((args.fruit_pack, args.sfx_pack, args.font)):
        parser.error("Use --from-build or the individual source options, not both")
    if args.from_build:
        restore_build(args.from_build)
    if args.fruit_pack:
        target = ROOT / "art" / "kawaii"
        target.mkdir(parents=True, exist_ok=True)
        contents = [(name, read_named(args.fruit_pack, name + ".svg")) for name in FRUITS]
        for name, content in contents:
            (target / (name + ".svg")).write_bytes(content)
        for script in ("build_kawaii_assets.py", "build_expressions.py", "build_emotions.py"):
            run(script)
    if args.sfx_pack:
        with tempfile.TemporaryDirectory(prefix="fruit-sfx-") as directory:
            folder = Path(directory)
            for name in SFX:
                (folder / name).write_bytes(read_named(args.sfx_pack, name))
            run("import_audio.py", "--sfx", folder)
    if args.font:
        if args.font.suffix.lower() != ".ttf" or not args.font.is_file():
            parser.error("--font must point to a downloaded .ttf file")
        shutil.copyfile(args.font, ROOT / "fonts" / "MouldyCheeseRegular-WyMWG.ttf")
    return check()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, zipfile.BadZipFile, subprocess.CalledProcessError) as error:
        print(f"Asset setup failed: {error}", file=sys.stderr)
        raise SystemExit(1)
