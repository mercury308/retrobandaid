import os
from typing import Dict, Optional

from src.core.checksum import calculate_checksums
from src.detection.database import lookup_by_crc32, system_for_extension
from src.detection.metadata import RomMetadata
from src.systems import arcade, compressed_media, disc, gba, modern_consoles, n64, nds, ps1, ps2, snes

# Ordered so more specific/cheaper checks run before broad ones (arcade zips, compressed media).
SYSTEM_MODULES: Dict[str, object] = {
    "snes": snes,
    "n64": n64,
    "gba": gba,
    "nds": nds,
    "ps1": ps1,
    "ps2": ps2,
    "arcade": arcade,
    "compressed_media": compressed_media,
    "modern_consoles": modern_consoles,
}

# 8MB covers every SNES cartridge (max 6MB) so snes.identify()'s size-based check stays
# correct even before the system is known; every other module's identify() only looks
# at fixed-offset magic bytes well within this range.
HEADER_SNIFF_SIZE = 8 * (1 << 20)

# These modules' has_header() inspects the *total* file length (copier-header/sector-size
# heuristics), so they need the real file size rather than a truncated sniff.
_SIZE_DEPENDENT_SYSTEMS = {"snes", "ps1"}


def identify_system(file_path: str) -> Optional[str]:
    """
    Guesses which systems.* module applies to a file: first trust the extension,
    verifying it with that module's identify(); otherwise probe every module in order.
    """
    extension = os.path.splitext(file_path)[1]
    with open(file_path, "rb") as f:
        sniff = f.read(HEADER_SNIFF_SIZE)

    hinted = system_for_extension(extension)
    if hinted and hinted in SYSTEM_MODULES and SYSTEM_MODULES[hinted].identify(sniff):
        return hinted

    for name, module in SYSTEM_MODULES.items():
        if module.identify(sniff):
            return name

    return None


def identify(file_path: str) -> RomMetadata:
    """Builds full RomMetadata for a file: system guess, header detection, and checksums."""
    system = identify_system(file_path)
    size = os.path.getsize(file_path)
    extension = os.path.splitext(file_path)[1]

    has_header = False
    if system and system in SYSTEM_MODULES:
        if system in _SIZE_DEPENDENT_SYSTEMS:
            with open(file_path, "rb") as f:
                probe = f.read()  # full read: has_header() for this system depends on total size
        else:
            with open(file_path, "rb") as f:
                probe = f.read(HEADER_SNIFF_SIZE)
        has_header = SYSTEM_MODULES[system].has_header(probe)

    checksums = calculate_checksums(file_path)
    known_name = lookup_by_crc32(checksums.get("crc32", ""))

    return RomMetadata(
        path=file_path,
        system=system,
        size=size,
        extension=extension,
        has_header=has_header,
        checksums=checksums,
        known_name=known_name,
    )
