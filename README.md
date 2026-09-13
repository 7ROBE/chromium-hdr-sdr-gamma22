# Gamma22Tray — Chromium HDR SDR Gamma 2.2

Gamma22Tray corrects ordinary SDR rendering in **normally installed 64-bit
Google Chrome and Microsoft Edge** while Windows HDR is enabled. It keeps the
browsers on their native HDR/scRGB presentation path but interprets ordinary
BT.709/sRGB SDR content using pure gamma 2.2.

> **[Download Gamma22Tray v0.5.0-beta.1 — Edge 153 support](https://github.com/mrsaliericz/chromium-hdr-sdr-gamma22/releases/tag/v0.5.0-beta.1)**

Portable or isolated browser copies are not required. Gamma22Tray runs in the
Windows notification area and applies the correction only in process memory;
it does not modify Chrome or Edge files on disk.

> **New beta — 13 September 2026:** Fixes **Unsupported/Error** with Edge
> `153.0.4234.32`. The new Edge output analyzer decodes x64 instructions and
> follows arguments and branches, allowing verified changes in registers,
> stack offsets and code placement instead of requiring one exact byte pattern.
> The author has confirmed correct SDR, Display-P3 and HDR video rendering in
> everyday testing. Its resilience through future browser updates still needs
> real-world testing; this is not a promise of support for every future version.

Chrome support from v0.4.3 is retained. The new analyzer specifically addresses
Edge's changed HDR output loop. See [Browser updates](#browser-updates) for the
remaining compatibility checks.

> **Free and open source, forever.** You may use, share, modify and redistribute
> this MIT-licensed project at no cost. If it improves your Windows HDR setup,
> you can optionally [buy me a coffee ☕](https://buymeacoffee.com/mrsaliericze).

## What it preserves

The correction is deliberately limited to ordinary SDR BT.709/sRGB content:

- Display-P3 and other wide-gamut content remains wide gamut.
- Native HDR video remains on Chromium's original HDR path.
- PQ, HLG, HDR black levels and highlights are not changed.
- SDR appearance remains stable when HDR or P3 content appears or disappears.
- Chrome and Edge browser files remain untouched on disk.

## Requirements

- Windows 11 x64 with Windows HDR enabled.
- Normally installed 64-bit Google Chrome and/or Microsoft Edge.
- A structurally compatible Chromium build. Unknown layouts are rejected
  before Gamma22Tray writes anything to process memory.

## Install and run

1. Download `Gamma22Tray-win64.zip` from the
   [v0.5.0-beta.1 release](https://github.com/mrsaliericz/chromium-hdr-sdr-gamma22/releases/tag/v0.5.0-beta.1).
2. Extract the **complete `Gamma22Tray` folder** to a permanent location.
3. Keep `Gamma22Tray.exe` beside its `_internal` folder. Copying the EXE alone
   will cause a missing Python DLL error.
4. Run `Gamma22Tray.exe` normally. Do not use **Run as administrator**.
5. Start or continue using the normally installed Chrome or Edge.

The tray icon is colored while the correction is enabled and gray while it is
disabled. Right-click it to access:

- **Disable/Enable Gamma 2.2 fix**
- **Start with Windows**
- **About Gamma22Tray**
- **Open diagnostic log**
- **Exit**

Turning the fix off restores upstream code and cached SDR color objects in
running browser processes. Exiting Gamma22Tray does not undo changes already
made in an existing process; disable the fix first or close the browser. All
in-memory changes disappear naturally when the browser exits.

## Browser updates

Gamma22Tray checks the installed Chrome and Edge DLL generations every five
seconds. When it recognizes a compatible update, it:

1. suspends new process-memory writes,
2. waits 15 seconds for the browser update to settle,
3. safely restarts itself,
4. attaches to the current browser generation.

As of **27 August 2026**, the project author's everyday testing has confirmed
continued functionality through **multiple successive updates of both Chrome
and Edge**. The correction resumed automatically after the updates, without
manual intervention or repatching.

Edge `152.0.4191.53` subsequently changed the recognized singleton layout from
98 to 97 sRGB initializers. Gamma22Tray v0.4.2 adds support for this layout and
checks that every associated sRGB load and singleton store is accounted for.
Older Gamma22Tray versions safely report **Unsupported/Error** for this Edge
build and need to be updated; restarting the old patcher alone will not help.

Chrome `153.0.8010.37` changed two stack-frame offsets immediately before its
HDR output helper call. Gamma22Tray v0.4.3 no longer identifies this location
using those fixed offsets. It instead requires a unique verified helper,
direct call target, argument-setup structure and original hook bytes. The
updated discovery was tested against unmodified Chrome 151, 152 and 153 DLLs;
unknown or ambiguous layouts are still rejected before any write occurs.

This confirms compatibility with the updates tested so far, not every future
Chromium layout. Unfamiliar layouts still fail closed and are reported in the
diagnostic log.

### More resilient Edge output analysis (v0.5.0 beta)

Edge `153.0.4234.32` moved output setup into a split code block and changed how
registers carry the usage table and output arguments. The previous byte pattern
could no longer identify it even though the 97 sRGB initializers still matched.

The beta adds a bounded instruction analyzer using Capstone. When the existing
Edge output pattern does not match, it uses PE function boundaries, identifies
the exact known output helper, and checks both supported control-flow paths.
It traces the usage-table value and output arguments, verifies the loop limit,
and verifies the analyzed function bytes again in the loaded process before
applying the correction. Unsupported instructions and ambiguous candidates are
rejected.

Tests cover changed stack offsets and loop registers, plus invalid calls,
tables, counters, arguments and branches. Read-only validation also passed for
the available original Edge 151 and Chrome 153 DLLs. Live inspection of two
Edge 153 browser/GPU pairs confirmed the intended role-specific changes, and
the author confirmed the visual result.

This improves tolerance of the supported compiler variations. It does not
remove the existing 97/98 Edge initializer-count checks, the exact output-helper
check or all other layout constraints. A different rendering implementation
can still require an update to Gamma22Tray.

## Start with Windows

Use **Start with Windows** in the tray menu after placing the extracted folder
in its permanent location. Gamma22Tray creates only this per-user registry
value and does not require administrator rights:

```text
HKCU\Software\Microsoft\Windows\CurrentVersion\Run\Gamma22Tray
```

Do not move or rename the extracted folder afterward. To change its location,
disable Start with Windows, move the complete folder, run the EXE from the new
location and enable the option again.

## Using it with dwm_eotf_rs

Gamma22Tray works well alongside
[`dwm_eotf_rs`](https://github.com/SERGEYDJUM/dwm_eotf_rs), and using both is
recommended when you want gamma correction in other Windows applications too.

Chromium remains on its HDR/scRGB presentation path, so `dwm_eotf_rs` does not
apply a second correction to the browser. Gamma22Tray handles Chromium's
internal SDR-to-scRGB conversion while `dwm_eotf_rs` continues handling other
SDR applications that pass through the Windows DWM path.

Gamma22Tray targets gamma **2.2**, not 2.4. There is currently no 2.4 mode.

## Browser video

- Native HDR video is not modified.
- Ordinary SDR video follows Chromium's active video/compositor path and may
  briefly change appearance when player UI or overlays appear.
- NVIDIA RTX Video HDR can convert supported SDR video to HDR before the final
  presentation path. When it is active, Gamma22Tray intentionally leaves that
  HDR result unchanged.

## HDR photos and Google Photos

Gamma22Tray intentionally does not modify HDR gain-map reconstruction or
Display-P3 images. Services can supply an iPhone photo as an Ultra HDR JPEG
with a P3 or sRGB SDR base plus a separate gain map. Its shadows and midtones
may therefore differ from Apple Photos or iCloud even while HDR highlights and
wide gamut remain active. This is outside the ordinary BT.709/sRGB path changed
by Gamma22Tray.

## Antivirus notice

Gamma22Tray is unsigned and necessarily uses Windows debugger attachment and
process-memory writes. Antivirus products can classify those behaviors as
suspicious even when the program was built from this published source.

The current release uses an unpacked **onedir** package because the earlier
self-extracting one-file beta triggered Windows Defender heuristics. It also
limits failed debugger attachments and skips incompatible WebView processes to
avoid retry storms.

Do not disable Windows security. Download only from this repository, verify the
published SHA-256, inspect the source, and build it yourself if in doubt.

## Diagnostics

Use **Open diagnostic log** in the tray menu. The log is stored at:

```text
%LOCALAPPDATA%\ChromiumGamma22\Gamma22HotAttach.log
```

Useful messages include the detected browser version and DLL hash, successful
browser/GPU process attachment, an update-triggered restart, or a safely
rejected unsupported layout.

## Build from source

Install Python 3.9 or newer and PyInstaller, then run:

```powershell
python -m pip install pyinstaller
python -m pip install -r requirements.txt
.\build_hot_attach_exe.ps1
```

The build produces:

```text
dist\Gamma22Tray-win64.zip
```

The GitHub release workflow runs the automated tests, builds the onedir ZIP and
publishes its SHA-256 together with the exact source commit.

## Safety model

- Browser binaries are never modified on disk.
- Candidate DLL layouts are structurally verified before runtime writes.
- Unknown or incompatible layouts fail closed.
- Attach retries are bounded to avoid repeated debugger activity.
- Only browser and GPU roles receive their corresponding changes; renderer and
  utility processes retain upstream behavior.

## Project information

- Author: Jaroslav Safar
- Contact: `jaroslav.safar.91@gmail.com`
- License: [MIT](LICENSE)
- Recommended test release: [Gamma22Tray v0.5.0-beta.1](https://github.com/mrsaliericz/chromium-hdr-sdr-gamma22/releases/tag/v0.5.0-beta.1)
- Previous stable release: [Gamma22Tray v0.4.3](https://github.com/mrsaliericz/chromium-hdr-sdr-gamma22/releases/tag/v0.4.3) (does not support the new Edge 153 output layout)

Historical documentation for the retired version-specific workflows is kept
in [`archive/LEGACY_VERSION_SPECIFIC_PATCHER.md`](archive/LEGACY_VERSION_SPECIFIC_PATCHER.md).
