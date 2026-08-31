# RetroBandaid

A lightweight ROM/disc-image patcher with a Tkinter GUI. Applies patch files to ROM dumps,
automatically handling console-specific quirks (copier headers, byte-order swaps) so you don't
have to strip/restore them by hand.

## Features

- **Patch formats:** IPS, BPS, UPS, PPF (v1/v2/v3), APS, xdelta/VCDIFF, BSDiff
- **System-aware patching:** automatically strips/restores headers for supported systems before
  and after patching, so patches made against a headerless ROM still apply to a headered dump
  - SNES copier headers (.smc)
  - N64 byte-order conversion (.z64/.v64/.n64)
  - GBA, PS1 (BIN/CUE + ISO), PS2, MAME-style arcade zips (detection/inspection helpers)
  - PSP CISO decompression; CHD and encrypted modern-console containers (Switch/3DS) are detected
    but explicitly unsupported for direct byte patching — see "Limitations" below
- **Checksums:** CRC32, MD5, SHA256 for verifying source ROMs
- **Simple Tkinter GUI:** pick a source ROM + patch file, apply, done

## Requirements

- Python 3.9+
- `pip install -r requirements.txt` (only needed for running the test suite; the app itself has
  no third-party runtime dependencies — the GUI uses the standard library's `tkinter`)
- Optional, only if you need these formats: `xdelta3` and `bspatch` must be installed and on your
  `PATH` (they're invoked as external processes; there is no pure-Python fallback)

## Usage

```powershell
python main.py
```

This launches the GUI: choose a source ROM, a patch file, and where to save the patched output,
then click **Apply Patch**. Use **ROM Info** to inspect a ROM's detected system, header, and
checksums before patching.

## Running tests

```powershell
python -m pytest tests/ -v
```

## Project layout

```
src/
  core/       # Patcher base class, checksum calculation, RomManager orchestrator
  formats/    # One module per patch format + PatchFactory
  systems/    # Per-console header stripping/byte-order handling
  detection/  # ROM identification (system guessing + metadata)
  gui/        # Tkinter application
  utils/      # Logging, config, async worker, shared header helpers
tests/        # pytest suite
```

## Limitations

- CHD and other compressed disc containers must be decompressed with an external tool (e.g.
  `chdman extractcd`) before patching — direct patching of compressed containers isn't supported.
- Switch (NSP/XCI) and 3DS (3DS/CIA) titles are encrypted/signed containers; byte-level patching
  is not supported and would corrupt them. Use dedicated tools for those platforms.
- PS1 raw BIN sector reconstruction preserves original sync/EDC/ECC bytes rather than
  recomputing them, which is fine for most emulators but not strictly spec-correct if a patch
  changes sector contents.
