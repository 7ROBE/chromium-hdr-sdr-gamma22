## Gamma22Tray v0.4.2 — Edge 152 compatibility

This release fixes **Unsupported/Error** after updating Microsoft Edge to
`152.0.4191.53`. The new DLL contains 97 recognized sRGB singleton initializers
instead of 98, so older Gamma22Tray releases safely reject it.

### What changed

- Supports the verified 97-initializer Edge 152 layout as well as the existing
  98-initializer layout used by Edge 151.
- Adds completeness checks for all loads of the canonical sRGB constant and
  all stores to its singleton. A partially recognized 98-initializer layout
  must not be mistaken for a valid 97-initializer layout.
- Retains the unique factory/pointer, gamut, transfer-function and scRGB/F16
  output-layout checks. Other counts and unsupported layouts remain rejected.
- Does not change the gamma curve, Chrome discovery, or native HDR/P3
  processing. Browser/GPU role separation and in-memory-only patching are
  unchanged.

### Updating

1. Download `Gamma22Tray-win64.zip` below and extract the complete folder.
2. Exit the older Gamma22Tray from its tray menu.
3. Replace the application's files with the complete new package. Keep
   `Gamma22Tray.exe` beside its `_internal` folder.
4. Run `Gamma22Tray.exe` normally, not as administrator.

If Start with Windows is enabled, keep the same installation path or update
that option after moving the application. Existing Edge windows can remain
open; the new version attaches to them without a browser restart.

Restarting an older Gamma22Tray release does not resolve this layout change.
Future Chromium layout changes may still require another compatibility update.

### Validation

- All 30 automated tests pass, including synthetic PE fixtures for both known
  counts, unknown counts, incomplete recognition, ambiguous constants,
  mismatched singleton targets and malformed output loops.
- Read-only layout validation passes for installed Edge `152.0.4191.53` and
  Chrome `152.0.7977.65`.
- Live memory inspection of two Edge browser/GPU pairs confirms exactly two
  output patches per browser process and 97 gamma initializer patches per GPU
  process. All out-of-role entries and shared color/helper checks remain
  unchanged.

### Safety

The package remains an unpacked onedir build. Gamma22Tray is unsigned and uses
debugger attachment and process-memory writes, which can trigger antivirus
heuristics. Do not disable security software; verify the published SHA-256 and
review the source or build it yourself if in doubt.

Browser files on disk are never patched. The project remains free, open source
and MIT-licensed.
