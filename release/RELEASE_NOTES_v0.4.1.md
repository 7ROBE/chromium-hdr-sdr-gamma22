## Gamma22Tray v0.4.1 — reliable live Edge attachment

Gamma22Tray v0.4.1 fixes a case where the tray could report **Active** even
though an already running Microsoft Edge browser and GPU process had not been
patched. The correction now resumes reliably without restarting Edge.

### What changed

- Adds a structurally verified in-memory image scan when Windows does not
  provide a usable `msedge.dll` load event during live debugger attachment.
- Ignores unrelated Microsoft Edge WebView2 debug events instead of mistaking
  their `msedge.dll` for the browser DLL.
- Reports **Active** only after the required browser and GPU processes have
  both been successfully verified and patched.
- Continues to fail closed when no known Chromium layout can be verified.
- Keeps browser and GPU changes separated: the browser receives only the
  scRGB/F16 output correction, while the GPU process receives only the SDR
  gamma 2.2 reinterpretation.

### Download and usage

1. Download `Gamma22Tray-win64.zip` below.
2. Extract the complete `Gamma22Tray` folder to a permanent location.
3. Keep `Gamma22Tray.exe` beside its `_internal` folder.
4. Exit an older Gamma22Tray version and run the new `Gamma22Tray.exe`
   normally. Running as administrator is not required.

Existing Chrome or Edge windows do not need to be restarted. Gamma22Tray
attaches to their current browser and GPU processes in memory.

### Validation

- 22 automated tests cover patch recipes, update generations, safe restart,
  bounded attachment, Edge WebView filtering, verified tray status and the
  in-memory fallback.
- Verified on Windows 11 x64 with Windows HDR enabled.
- Verified against Google Chrome `151.0.7922.174` and Microsoft Edge
  `151.0.4129.101`.
- A live memory audit confirmed exactly two scRGB/F16 output writes in the Edge
  browser process and 98 gamma 2.2 initializer writes in its GPU process, with
  no unexpected changes.
- Native HDR video, HDR black levels, PQ/HLG and Display-P3 remain unchanged.

### Antivirus note

Gamma22Tray remains unsigned and necessarily uses debugger attachment and
process-memory writes, which can trigger antivirus heuristics. This release
uses the unpacked onedir package introduced in v0.4.0. Do not disable Windows
security; download only from this repository, verify the published SHA-256 or
build the application from source if in doubt.

- Author: Jaroslav Safar
- Contact: `jaroslav.safar.91@gmail.com`
