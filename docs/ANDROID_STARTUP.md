# Android startup correction: 0.2.3

## Observed failure

The 0.2.2 phone report shows SIGSEGV while loading the main game assets.
Symbolication against the exact Defold 1.13.1 ARM64 engine resolves the relevant frames:

| Relative PC | Function |
| --- | --- |
| `0x12b6dc` | `dmGraphics::OpenGLSetTexture` |
| `0x139a38` | `dmGraphics::AsyncProcessCallback` |
| `0x3087dc` | `ProcessOneJob` |
| `0x307c18` | `JobThread` |

The vendor stack includes `glTexImage2D`. The frame addresses above come from the native
report's **Details** section, which has the correct module-relative addresses. The earlier
nearest-module summary can misidentify Android libraries mapped directly from the APK.

## Confirmed packaging defect

The atlas header in the delivered 0.2.2 APK declares a 4096 x 4096 RGBA image with
67,108,864 payload bytes. Its archived entry decompresses to only 20,971,520 total bytes:
49 header bytes plus **20,971,471 payload bytes**. It is truncated by 46,137,393 bytes.
This gives the graphics upload a data pointer whose available allocation is smaller than
the image it is asked to read, consistent with the observed driver crash.

The source PNG assets are intact. The invalid file was a reused compiled build output;
this investigation does not establish how that cache file originally became truncated.
The previous render tests used fresh isolated builds, so they did not exercise that bad
cached output when Android packaging reused it.

## Correction and verification

`tools/build_android_local.py` now copies source into a fresh temporary project, retains
only downloaded dependencies, and rebuilds every resource before packaging. It continues
to use the same matching OpenGL ES engine and local signing identity.

`tools/VerifyTexturePayloads.java` decodes the actual APK archive index, decompresses each
archived texture, parses its header with the matching Bob protobuf definitions, and rejects
payload lengths that differ from the header. The build checks the resource archive, finished
APK, and exported APK; it does not rely on the size of an intermediate source file.

Validation performed:

- The guard rejects the delivered 0.2.2 APK for the exact short payload above.
- The 0.2.3 APK contains the full 67,108,864-byte atlas payload.
- APK version 0.2.3 / code 4 and v1/v2/v3 signatures verify; the update certificate matches.
- The native engine bytes and adaptive icon resources are unchanged.
- Desktop OpenGL recovery, report navigation, gameplay rendering, and touch/drop checks pass.

The on-device retest is still needed. This corrects the confirmed corrupt resource; desktop
rendering cannot establish that there are no additional phone-specific problems.
Install over the previous app and tap **Try game** if the old crash recovery screen appears.

Manual archive validation (use the same Bob version as the game):

```sh
java -Dcom.google.protobuf.use_unsafe_pre22_gencode -cp /path/bob.jar tools/VerifyTexturePayloads.java --apk /path/FreakyFruitFusion.apk
```
