## Gamma22Tray v0.6.0 — Chrome, Edge and Brave

This stable release adds **Brave** and includes the more resilient Edge 153
output analyzer previously tested in v0.5.0-beta.1. One tray application now
monitors normally installed 64-bit Google Chrome, Microsoft Edge and Brave.

### What changed

- Detects Brave Stable in standard Program Files and per-user LOCALAPPDATA
  installation directories. Custom paths and Beta/Nightly channels are not
  automatically detected.
- Uses the existing Chrome analyzer for Brave's `chrome.dll`; no matching rules
  were loosened to accept Brave.
- Includes Brave in browser/GPU process monitoring, the on/off control and
  update handling, and adds it to the About text.
- Retains the bounded Edge instruction analyzer, which verifies arguments and
  branches despite supported changes in registers, stack offsets and code
  placement. Unknown layouts still fail closed.

Ordinary BT.709/sRGB SDR receives pure gamma 2.2. Native HDR video, PQ, HLG and
Display-P3 processing are unchanged by this release. Browser files on disk are
never modified. The tool can be used alongside `dwm_eotf_rs` as before.

### Validation and compatibility

- All 39 automated tests pass.
- Brave 1.95.101 (installation directory `153.1.95.101`) passed existing Chrome
  layout checks. Independent live-memory inspection confirmed 94 gamma writes
  in its GPU process and two output writes in its browser process, with zero
  mismatches and an unchanged DLL hash on disk.
- The author confirmed the visual result in Brave before approving release.
- The preceding Edge analyzer was tested on Edge `153.0.4234.32`, with backward
  read-only validation on the available original Edge 151 DLL. Chrome
  `153.0.8010.37` compatibility was also verified.

Stable release status does not guarantee support for every future browser
layout. The existing Edge initializer-count and exact-helper checks remain.
The new Edge analyzer's resilience and Brave update recovery still need
real-world testing through subsequent updates.

### Install or update

1. Download `Gamma22Tray-win64.zip` below and extract the complete folder.
2. Exit the previous Gamma22Tray from its tray menu.
3. Replace the application's files with the complete new package. Keep the
   EXE beside `_internal`, including the bundled Capstone library.
4. Run `Gamma22Tray.exe` normally; administrator rights are not required.

Browsers can remain open. If using **Start with Windows**, keep the same
installation path or reconfigure that option after moving the application.
The tray menu also provides on/off control, About and the diagnostic log.

### Source and distribution

Source builds require Python, PyInstaller and `pip install -r requirements.txt`.
The package is built by GitHub Actions with its source commit and SHA-256
published below. Gamma22Tray is unsigned and uses debugger attachment and
process-memory writes, which can trigger antivirus heuristics. Do not disable
Windows security.

Gamma22Tray is free and MIT-licensed; bundled dependencies retain their own
licenses. Optional support: https://buymeacoffee.com/mrsaliericze
