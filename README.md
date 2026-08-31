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
  - **Windows:** the official python.org installer bundles `tkinter` already.
  - **Linux:** `tkinter` is usually a separate package — install it first, e.g.
    `sudo apt install python3-tk` (Debian/Ubuntu) or `sudo dnf install python3-tkinter` (Fedora).
- `pip install -r requirements.txt` (only needed for running the test suite or building a
  standalone binary; the app itself has no third-party runtime dependencies)
- Optional, only if you need these formats: `xdelta3` and `bspatch` must be installed and on your
  `PATH` (they're invoked as external processes; there is no pure-Python fallback)
  - Windows: `choco install xdelta3` or download prebuilt binaries manually
  - Linux: `sudo apt install xdelta3 bsdiff` (Debian/Ubuntu) or your distro's equivalent

## Installation

Pick whichever fits you — both are fully supported on Windows and Linux.

### Option A: Run from source (requires Python)

```bash
git clone https://github.com/mercury308/retrobandaid.git
cd retrobandaid
python main.py
```

No `pip install` is required just to run the app — only for tests/building (see below).

### Option B: Standalone binary (no Python required for the end user)

Build it yourself once (see "Building a standalone executable"), then hand the resulting binary
to anyone — they don't need Python or any dependencies installed.

## Usage

Whichever way you launch it, the GUI works the same: choose a source ROM, a patch file, and where
to save the patched output, then click **Apply Patch**. Use **ROM Info** to inspect a ROM's
detected system, header, and checksums before patching.

## Running tests

```bash
python -m pytest tests/ -v
```

## Building a standalone executable (Windows or Linux)

```bash
pip install -r requirements.txt
pyinstaller pyinstaller.spec --noconfirm
```

Bundles Python, `tkinter`, and `medicon.png` into a single windowed binary in `dist/`:
- Windows: `dist/RetroBandaid.exe`
- Linux: `dist/RetroBandaid` (run with `./dist/RetroBandaid`; you may need `chmod +x` first)

Run the build command on the OS you want a binary for — PyInstaller doesn't cross-compile.
`xdelta3`/`bspatch` are still separate system tools and must be installed independently on the
target machine if those formats are needed.

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
