## Gamma22Tray v0.5.0-beta.1 — Edge 153 and more resilient output analysis

Fixes **Unsupported/Error** with Microsoft Edge `153.0.4234.32` and retains
Chrome support from v0.4.3. Standard installed 64-bit Chrome and Edge are
supported; portable copies are not required.

### What changed

Edge changed registers and split the HDR output loop into a different code
block. The beta adds a bounded x64 instruction analyzer using Capstone rather
than adding another exact byte pattern for this build.

The analyzer verifies the known output helper, traces usage-table values and
output arguments through both supported branches, and checks the loop limit.
Before writing to a process, Gamma22Tray rechecks the analyzed function bytes.
Unknown instructions, unsupported control flow and ambiguous candidates are
rejected. Existing Edge initializer checks and Chrome discovery remain intact.

This should tolerate more compiler variations, but compatibility with future
browser updates remains to be tested. The existing 97/98 Edge initializer-count
and exact-helper checks remain in place. This is deliberately a **beta**.

### Validation

- All 39 automated tests passed, including variations in stack offsets and
  loop registers and rejection of invalid calls, tables, counters and branches.
- Read-only plan validation passed for Edge `153.0.4234.32`, the available
  original Edge 151 DLL and Chrome `153.0.8010.37`.
- Independent live-memory inspection of two Edge 153 browser/GPU pairs
  confirmed 97 gamma writes per GPU process and two output writes per browser
  process. Out-of-role entries and all evidence checks remained unchanged.
- The Edge DLL hash on disk remained unchanged.
- The author confirmed the visual result in everyday use before publication.

Ordinary SDR BT.709/sRGB receives the gamma 2.2 correction. Native HDR video,
PQ, HLG and Display-P3 processing are not changed by this compatibility update.

### Install or update

1. Download `Gamma22Tray-win64.zip` below and extract the complete folder.
2. Exit the previous Gamma22Tray from its tray menu.
3. Replace the application's files with the complete new folder. Keep the EXE
   and `_internal` directory together, including the bundled Capstone library.
4. Run `Gamma22Tray.exe` normally. Administrator rights are not required.

Chrome and Edge can remain open. If using **Start with Windows**, keep the
installation path unchanged or reconfigure that option after moving it.
The tray menu includes the on/off switch, startup option, About and diagnostic
log. The tool works alongside `dwm_eotf_rs` as before.

### Source and safety

Source builds now also require `pip install -r requirements.txt`. Capstone is
pinned to 5.0.6 and included in the downloadable onedir package.

Gamma22Tray remains unsigned and uses debugger attachment and process-memory
writes, which can trigger antivirus heuristics. Do not disable Windows
security. The published SHA-256 identifies the GitHub Actions package.
Browser files on disk are never patched. Gamma22Tray remains free and
MIT-licensed; bundled dependencies retain their own licenses.
