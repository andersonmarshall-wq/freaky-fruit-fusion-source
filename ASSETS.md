# Local asset setup

The public repository contains the game code, UI resources, original effects,
launcher artwork, synthetic voices, and the two attributed CC BY 4.0 music tracks.
The RDBI fruit vectors and all derived fruit sprites are excluded. Six Candle Light
sound effects and the separately licensed font are also obtained locally.

The original APK's appearance and behavior are preserved after local asset setup.
The public source is not a standalone asset pack. A fresh clone needs the following
files before Defold can build the game.

| Source | What to obtain | Use in this project |
| --- | --- | --- |
| [RDBI — Kawaii Fruits](https://rdbi.itch.io/kawaii-fruits) | Purchase and download `ItchIO_File.zip` | Nine base vectors; scripts generate twelve tiers and expression variants |
| [Candle Light — Tiny Pops & Sparkles](https://candlelightgame.itch.io/tiny-pops-sparkles-80-free-game-sfx) | Download `Tiny_Pops_and_Sparkles_Free_80_SFX.zip` | Six quiet game effects |
| [Niskala Huruf — Mouldy Cheese](https://www.fontspace.com/mouldy-cheese-font-f95405) | Download and extract the Regular TTF | Interface font; the author permits commercial projects |
| [chajamakesmusic — cute & silly rpg music pack](https://chajamakesmusic.itch.io/cute-and-silly-rpg-music-pack) | Already included as two adapted OGG files | CC BY 4.0; see `CREDITS.md` for attribution and changes |

Install Python 3, Pillow, Inkscape, and FFmpeg with Vorbis support. After obtaining
the files from their creators, run:

```sh
python3 -m pip install Pillow
python3 tools/import_local_assets.py \
  --fruit-pack /path/to/ItchIO_File.zip \
  --sfx-pack /path/to/Tiny_Pops_and_Sparkles_Free_80_SFX.zip \
  --font /path/to/MouldyCheeseRegular-WyMWG.ttf
```

ZIPs may remain outside this repository. The importer reads only the expected
filenames and does not extract arbitrary archive paths. It runs the existing
fruit/expression generation and audio conversion scripts.

If you maintain your own complete licensed 0.2.1 project, restore its local assets:

```sh
python3 tools/import_local_assets.py --from-build /path/to/complete-project
```

This checks the reference hashes before copying the 225 omitted files. For edits
to your own local assets, `--check` verifies the required files are present without
requiring the original hashes:

```sh
python3 tools/import_local_assets.py --check
```

Then open `game.project` in Defold 1.13.1 and build normally. Source-level gameplay
and squish tests can run without the asset packs. Engine/render tests need setup.

## Publishing changes

`assets.local.json` lists omitted files and reference hashes, not asset contents.
`.gitignore` excludes the raw fruit vectors, expression variants, generated fruit
PNGs, preview image, six effect files, font, archives, and build/signing outputs.
Before committing or pushing, run:

```sh
python3 tools/check_public_source.py
```

Do not force-add ignored files. RDBI permits game use and modifications but prohibits
redistribution of the asset files. A credit does not replace that restriction.
Candle Light permits personal and commercial game use; its page does not explicitly
grant standalone asset redistribution. The font is linked to its creator's download
instead of being mirrored here. Purchased assets are not covered by the code's MIT
license. Share compiled games only under the applicable asset terms.
