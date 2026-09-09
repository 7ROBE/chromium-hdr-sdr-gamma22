## Gamma22Tray v0.4.3 — Chrome 153 compatibility

This release fixes **Unsupported/Error** after Google Chrome updated to
`153.0.8010.37`. Chrome changed two stack-frame offsets around the ScreenWin
HDR output setup, so the fixed instruction context used by earlier releases no
longer matched.

### What changed

- Discovers Chrome's SDR scRGB/F16 output hook structurally instead of relying
  on fixed stack-frame offsets.
- Requires one exact output helper, a direct call to that helper, the expected
  RCX/R9 argument-setup instructions and the untouched five hook bytes.
- Rejects missing, ambiguous or mismatched candidates before making any
  process-memory write.
- Retains compatibility with the verified Chrome 151 and 152 layouts.
- Does not change Edge discovery, the gamma curve, browser/GPU role separation
  or native HDR, PQ, HLG and Display-P3 processing.

### Updating

1. Download `Gamma22Tray-win64.zip` below and extract the complete folder.
2. Exit the older Gamma22Tray from its tray menu.
3. Replace the application's files with the complete new package. Keep
   `Gamma22Tray.exe` beside its `_internal` folder.
4. Run `Gamma22Tray.exe` normally, not as administrator.

If Start with Windows is enabled, keep the same installation path or enable
the option again after moving the application. Existing Chrome and Edge
windows can remain open; the new version attaches to them without a browser
restart.

### Validation

- All 36 automated tests pass, including synthetic Chrome 151/152 and Chrome
  153 output-hook layouts plus rejection tests for ambiguous or malformed
  candidates.
- Read-only discovery passes for unmodified installed Chrome
  `153.0.8010.37`: 47 BT.709/sRGB initializer pairs, the unique output hook and
  the verified trampoline cave are all recognized.
- Read-only backward-compatibility checks pass for available unmodified Chrome
  151 and 152 DLLs.
- Live Chrome 153 memory inspection confirms 94 gamma writes in the GPU
  process, two scRGB/F16 output writes in the browser process and no unexpected
  role-specific writes. The browser DLL on disk remains unchanged.
- The corrected SDR appearance, new tabs and native HDR video were confirmed
  in a real Chrome 153 session before release.

### Antivirus notice

Gamma22Tray is unsigned and necessarily uses debugger attachment and
process-memory writes. Those behaviors can trigger antivirus heuristics; a
locally built v0.4.3 candidate was classified by Windows Defender as
`Behavior:Win32/DefenseEvasion.A!ml` during testing. This behavior-based alert
does not establish that every build will be flagged, but users should treat
security warnings seriously.

Do not disable Windows security. Download only from this repository, verify
the release SHA-256, inspect the source and build it yourself if in doubt.
Browser files on disk are never patched. The project remains free, open source
and MIT-licensed.
