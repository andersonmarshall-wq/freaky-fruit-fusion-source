# Freaky Fruit Fusion — development notes

## Progression and materials

| Tier | Fruit | Sprite size | Relative softness |
| --- | --- | --- | --- |
| 1 | Cherry | 80 × 80 | 0.72 |
| 2 | Blueberry | 100 × 100 | 0.95 |
| 3 | Passion fruit | 125 × 125 | 0.40 |
| 4 | Kiwi | 140 × 140 | 0.64 |
| 5 | Orange | 165 × 165 | 0.46 |
| 6 | Peach | 190 × 190 | 1.00 |
| 7 | Coconut | 220 × 220 | 0.16 |
| 8 | Pineapple | 250 × 250 | 0.28 |
| 9 | Honeydew | 270 × 270 | 0.25 |
| 10 | Cantaloupe | 300 × 300 | 0.30 |
| 11 | Whole watermelon | 330 × 330 | 0.24 |
| 12 | Whole golden watermelon | 330 × 330 | 0.30 |

Material values are game-feel choices inspired by ripe fruit. Tune them in `logic/module/fruit_profiles.lua`.
Tier 12 uses the inherited filename `ball_11f`, but is a real separate tier and remains in the saved pile.
The purchased pack also contains `WatermelonHalf.svg`; no gameplay sprite uses it, and the public repository contains no purchased fruit vectors.

## Squish and pressure

Collision impulses produce a damped impact spring. Sustained contact load produces a slower resting strain,
including sideways pressure. Deformation is area-preserving and oriented along the stress direction.
The collision radius gradually contracts by up to 6.5%, letting the pile settle and open small gaps.
Soft peaches deform much more than coconuts. Removing a load lets the fruit recover.

This is a lightweight soft-body approximation: collision shapes remain circular, so a fruit cannot dent
independently at several contact points. The sprites deform more than the collider. Pressure is integrated
in `fixed_update` at the same 60 Hz step as physics, so it is independent of display refresh rate.
Sleeping bodies retain their loads only while their support contacts remain in place.

Pressure drives two stressed faces. Talking, directional kissing, and a one-and-a-half-second startled
shake expression are separate states. Art is generated from the editable vectors, with original outlines
and fruit colors retained. The golden halo gently pulses; it is not a strobe.

## Scoring and shake

A merge's base score is `2^(source tier - 1)`. Direct merges involving the dropped fruit are 1× and have
no chain word art. Further merges during a three-second cascade earn 2×, 3×, up to 5×. Pile-only merges
can start at 2×. Atomic registry removal prevents duplicate collision events from scoring twice.
Dropping or bursting fruit gives no points.

Shake requires three alternating acceleration peaks in 0.95 seconds after gravity filtering; normal tilts
and one bump are rejected. It has a ten-second cooldown. Tiny tiers 1–3 must be below y=980 and at least
0.85 seconds past their drop to burst. All remaining dynamic fruit receive bounded upward/sideways kicks.
Two seconds of overflow grace allow the pile to resettle. A hold button and Space provide alternatives.

## Audio

The supplied `blossom.wav` and `regrowth wip.wav` become slower, low-pass-filtered, loudness-normalized OGGs,
with four-second crossfades. The music continues across replay. Pops and sparkles use six selected effects
from Tiny Pops & Sparkles. Eight quiet synthetic gibberish clips and four short synthesized squeals provide
voices; they are not voice recordings from the purchased SFX pack. A bounded chorus avoids playing dozens
of screams at full volume. Exact musical suitability and mix levels need listening on the target phone.

## Regenerate assets

First follow `ASSETS.md` to restore locally licensed assets. To regenerate them, install Inkscape, Python/Pillow, FFmpeg with
Vorbis and Flite support, then run from this directory:

```sh
python3 tools/build_kawaii_assets.py
python3 tools/build_expressions.py
python3 tools/build_emotions.py
python3 tools/build_sounds.py
python3 tools/build_voices.py
```

`build_sounds.py` only rebuilds the original synthesized cues and measures existing music; it preserves the
purchased effects. To reimport audio from the owner's separately extracted packs:

```sh
python3 tools/import_audio.py --sfx /path/to/Tiny_Pops_and_Sparkles --music /path/to/poopie_pack
```

The mapping lives in `art/kawaii/mapping.csv`. Honeydew and cantaloupe adapt Cherry; the golden watermelon
adapts WatermelonFull. Expression sources and effects are native editable SVGs.

## Validation / next device check

Defold 1.13.1 compiles the complete project and bundles a signed ARM64 APK. LuaJIT tests cover spring
strength, direction, rebound, duplicate contact suppression, frame-rate stability, load retention/recovery,
material differences, cascade scoring, and motion filtering. The real headless engine passes the integrated
pile/scoring/shake test. A loaded peach measured about 0.091 logarithmic compression versus 0.012 for a
coconut; its center settled about 3 pixels below the rigid support height, and pressure activated stress.
All shipped OGGs decode successfully. The local art preview has been visually checked and is excluded from public source control.

The 0.2.1 phone retest showed the loading screen before the app closed itself. The exact native
failure is still unknown. Version 0.2.2 adds local crash recovery and paginated **Crash details**;
install over the previous app, reopen after any failure, and capture every report page.
It retains the OpenGL ES engine and existing load path so the device can supply failure evidence.
An explicit adaptive icon now supplies the foreground and peach background to Android launchers.

Version 0.2.2 passed actual OpenGL rendering and touch-position smoke tests at 1080 × 2424,
including a real synthetic engine dump, recovery navigation, retry, fruit drop, and credits panel.
The headless renderer substitutes a blank texture for the 4096-pixel atlas, so it verifies script
and physics behavior, not appearance. Physical Android startup remains unverified; diagnose the
phone report before tuning the mix, vigorous-shake threshold, or pile feel.
