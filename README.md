# Freaky Fruit Fusion

A kawaii fruit-merging game for Android, built with Defold.
Based on [Wateru by AsetSiya](https://github.com/asetsiya/wateru), with its MIT license retained.

**Public source, version 0.2.2 (diagnostic).** The paid fruit art and selected third-party assets
are supplied locally. See [ASSETS.md](ASSETS.md) before building.
Two matching fruits fuse into the next kind, ending in a **whole, glowing golden watermelon**.
There are no sliced watermelons in the playable progression.

## Play

Touch and drag to aim; release to drop. Merge matching fruit and keep the pile below the red line.
A direct merge scores normally. Secondary and tertiary merges earn increasing bonuses and
cheeky word art such as “Juicilicious!”, “So juicy!”, “Dripping!”, and “Moist!”.

Shake the phone vigorously three times in alternating directions, hold **SHAKE IT UP!**,
or press **Space** on desktop. Cherries, blueberries, and passion fruits already down in the
pile burst into juice; the remaining fruit bounce and the pile squeals. Recharges in 10 seconds.

The `...` button controls music, music volume, sound effects, smooches, and elf chatter,
and opens **Credits & creators** with links to the original itch.io packs.
The pile, current score, best score, and settings save locally. This prototype runs offline.

## What's in this version

**0.2.2 diagnostic build:** local crash recovery with a readable, paginated **Crash details**
screen, startup-stage breadcrumbs, and an adaptive Android launcher icon with a peach background.
Android version code 3 and the unchanged package/signing certificate allow updating earlier builds
in place. Install over the existing app to retain its crash report and saved game.
This is not yet a confirmed fix for the phone's startup crash.

A build you sign yourself requires your own package/signing setup; signing keys are not included.

- Twelve kawaii fruit tiers, including honeydew and cantaloupe; a pulsing halo surrounds the golden final tier.
- Impact squish and rebound, persistent load compression, gradual physical settling, and fruit-specific softness.
- Worried and strained faces under pressure; nearby matching fruit look toward each other and blow kisses.
- Quiet randomized synthetic elf-like gibberish and a bounded chorus of startled squeals during a shake.
- Gusher droplets, hearts, sparkles, cascade word art, and merge-only scoring with bonuses up to 5×.
- Two gentler ambient tracks from the supplied music pack, with four-second crossfades; soft pops and sparkles from the supplied SFX pack.

## Open or build

Open `game.project` with **Defold 1.13.1**. Let Defold resolve the pinned orthographic-camera dependency,
then Build / Run. First follow [ASSETS.md](ASSETS.md) to import your locally licensed fruit artwork, sound effects, and font. The attributed CC BY music and original effects are included.
For Android, choose **Project → Bundle → Android Application**, ARM64, debug, APK.
The project uses package `com.freakyfruit.fusion`. APKs and signing keys are not stored in this source repository.

The 0.2.0 APK showed a blank screen on the target phone. Version 0.2.1 switched to OpenGL ES,
disabled the Vulkan quality probe, and added an asynchronous loading screen. The new phone
recording confirms that screen appears before the app closes itself during startup. The exact
native failure remains unknown; desktop rendering does not establish Android compatibility.

Version 0.2.2 reads the engine's previous crash dump and pauses at a recovery screen. Open
**Crash details** and capture every page. If the app closes on its first launch, reopen it to
read the new report. **Try game** retries loading. Reports remain on the device; there is no
telemetry or automatic upload. If Android provided no native dump, the last startup stage is shown.

Recovery, native-dump decoding, report navigation, actual game rendering, and simulated
touch/drop input passed the desktop OpenGL smoke test at **1080 × 2424**. APK signatures,
update certificate, version, and adaptive-icon resources were checked. Physical-phone startup
and launcher appearance still need verification.

For local packaging with a separately built matching OpenGL ES engine, use
`tools/build_android_local.py --bob /path/bob.jar --java /path/java --engine /path/libdmengine.so --output /path/output`.
This compiles and packages the game's files locally, without a remote native build of this project.

## Checks

From this directory, with LuaJIT installed:

```sh
luajit tests/gameplay_test.lua
luajit tests/squish_test.lua
python3 tools/run_engine_tests.py --bob /path/to/bob.jar --java /path/to/java --engine /path/to/dmengine_headless
python3 tools/run_render_smoke.py --bob /path/to/bob.jar --java /path/to/java --engine /path/to/dmengine --xvfb /path/to/Xvfb --output /path/to/results --recovery-test
```

The engine test uses an isolated copy and separate save file. It exercises load compression,
real settling, pressure stress, duplicate collision safety, direct/secondary/tertiary scoring,
shake clearing, large-fruit bounce, panic animation, cooldown, and the final golden tier.

See [KAWAII_README.md](KAWAII_README.md) for tuning, asset mapping, and regeneration.
See [CREDITS.md](CREDITS.md) for asset sources and license distinctions. The code's MIT
license is retained in `LICENSE`; third-party art, music, effects, and fonts keep their
own terms. This repository starts with a clean public history that contains no restricted
fruit art. The complete asset-bearing development history is retained separately by the maintainer.

Before publishing changes, run `python3 tools/check_public_source.py` and keep local
assets out of commits. The original Wateru description is retained in `README_UPSTREAM.md`.
