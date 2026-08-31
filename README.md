# RetroBandaid

RetroBandaid is a byte-level patch-application engine for ROM dumps and disc images. It parses a patch file's binary format directly (no external patching libraries), reconstructs the target file byte-for-byte, and for consoles where patches are
distributed against a "clean" ROM, automatically strips a console-specific header before patching and restores it afterward, so you don't have to do that by hand with a hex editor.

<img width="750" height="400" alt="Screenshot 2026-08-30 212825" src="https://github.com/user-attachments/assets/3ec5af22-aa9d-46f9-b509-60493cdfb60d" />



## What it actually does

1. **Reads the patch file's binary format directly.** Each format in `src/formats/` implements
   the format's spec from scratch: record-based literal/RLE patching for IPS, variable-length
   integer decoding + delta-encoded copy/read commands for BPS, XOR-based diffing for UPS,
   record-based patching for PPF/APS, and subprocess delegation to `xdelta3`/`bspatch` for
   xdelta/VCDIFF and BSDiff (those two have no pure-Python implementation here).
2. **Identifies the ROM's target system** (`src/detection/rom_identifier.py`) by checking the
   file extension against a known table, then verifying with a system-specific magic-byte/
   checksum check (e.g. SNES internal header checksum, N64 magic bytes, GBA fixed header byte).
3. **Strips any console-specific header** (`src/systems/*.py`) before applying the patch, so a
   patch built against a headerless ROM still lines up correctly against a headered dump — then
   re-attaches it afterward. For N64, "header" instead means byte-order: the ROM is normalized to
   big-endian before patching and converted back to its original byte order afterward.
4. **Writes the patched output** to the path you choose, leaving the original source file
   untouched.

## Supported patch formats

| Format | Extension(s) | How it's applied |
|---|---|---|
| IPS | `.ips` | 3-byte big-endian offset + 2-byte size records, with RLE support (`size == 0`). |
| BPS | `.bps` | Variable-length integers; SourceRead/TargetRead/SourceCopy/TargetCopy commands. |
| UPS | `.ups` | XOR-based diff against the source, delta-encoded record offsets. |
| PPF | `.ppf` (v1/v2/v3) | Fixed-offset header, then offset+length+payload records. |
| APS | `.aps` | Standard (non-N64) mode only; N64-mode APS patches are rejected. |
| xdelta / VCDIFF | `.xdelta`, `.vcdiff` | Shells out to the `xdelta3` binary — must be installed and on `PATH`. |
| BSDiff | `.bsdiff`, `.bdf` | Shells out to the `bspatch` binary — must be installed and on `PATH`. |

`src/formats/factory.py` picks the right class by file extension and validates the patch's
magic bytes before handing it to `core/rom_manager.py`.

## Supported consoles / systems

| System | Module | What's handled |
|---|---|---|
| SNES | `systems/snes.py` | Detects/strips the 512-byte copier header (`.smc`); validates via the internal ROM checksum/complement pair at the LoROM/HiROM header offset. |
| N64 | `systems/n64.py` | Detects `.z64`/`.v64`/`.n64` byte order from magic bytes; normalizes to big-endian for patching, converts back afterward. |
| GBA | `systems/gba.py` | Validates the fixed header byte at offset `0xB2`; no header to strip. |
| Nintendo DS | `systems/nds.py` | Validates the cartridge header; patches the complete image and recalculates its header CRC16. |
| PS1 | `systems/ps1.py` | Detects raw 2352-byte BIN sectors vs. plain 2048-byte ISO sectors; can split/reassemble the sync+ECC sidecar around the 2048-byte data field for patching against ISO-style patches. |
| PS2 | `systems/ps2.py` | Detects 2048-byte-sector ISO9660 images; no header to strip. |
| Arcade (MAME-style) | `systems/arcade.py` | Lists/extracts/replaces individual chip-dump files inside a romset `.zip`. |
| PSP (CISO) | `systems/compressed_media.py` | Decompresses CISO-compressed UMD dumps (`decompress_ciso`). |

**Explicitly unsupported for direct byte patching** (detected, but patching is refused with a
clear error rather than silently producing a corrupt file):
- CHD and other compressed disc containers — decompress with an external tool first (e.g.
  `chdman extractcd`).
- Switch (NSP/XCI) and 3DS (3DS/CIA) — these are encrypted/signed containers. They are
  detected and explicitly rejected before byte-level patching could corrupt them.

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

1. Launch the app: `python main.py` (or run the built binary).
2. **Source ROM** → Browse to the original, unpatched ROM/disc image file.
3. **Patch File** → Browse to the `.ips`/`.bps`/`.ups`/`.ppf`/`.aps`/`.xdelta`/`.bsdiff` file you
   want to apply.
4. **Output ROM** → choose where the patched result should be written (the source file is never
   modified in place).
5. *(Optional)* Click **ROM Info** first to see the detected system, whether a copier header was
   found, and the CRC32/MD5/SHA256 of the source file — useful for confirming you have the right
   base ROM before patching.
6. Click **Apply Patch**. The status bar reports progress; a dialog confirms success or reports
   the specific error (e.g. wrong patch magic bytes, source ROM too small for a given offset).

## Running tests

```bash
python -m pytest tests/ -v
```

`tests/` covers binary round-trips for each pure-Python format (hand-constructed patch bytes
verified against expected output) plus SNES header stripping and N64 byte-order conversion.

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

## License

[MIT](LICENSE)



