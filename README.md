# Freaky Fruit Fusion

A kawaii fruit-merging game for Android, built with Defold.
Based on [Wateru by AsetSiya](https://github.com/asetsiya/wateru), with its MIT license retained.

**Public source, version 0.2.3.** The paid fruit art and selected third-party assets
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

**0.2.3:** repairs a truncated fruit atlas in the packaged APK. Android packaging now rebuilds
all resources from source in an isolated directory and checks the finished APK for complete
texture payloads. Local crash recovery and the adaptive peach launcher icon are retained.
Android version code 4 and the unchanged signing certificate permit an in-place update.
Tap **Try game** if the recovery screen still shows the previous crash.
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

The phone's 0.2.2 crash report identified a texture upload failure. Inspection of the actual
APK found a 4096 x 4096 RGBA atlas with only 20,971,471 of its required 67,108,864 payload
bytes. Version 0.2.3 rebuilds that atlas completely and rejects malformed textures before
publishing the APK. See [the investigation and verification](docs/ANDROID_STARTUP.md).

The new guard rejects the old APK and passes the repaired APK. Recovery navigation, actual
game rendering, and simulated touch/drop input pass the desktop OpenGL smoke test at
**1080 x 2424**. APK signatures and the matching update certificate are verified. An on-device
retest is still needed to confirm startup on the target phone.

Reports stay on the device. If a new failure occurs, reopen the app and capture all **Crash details**
pages. **Try game** retries loading without deleting the saved game.

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
