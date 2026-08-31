from typing import Dict, Optional

# Maps file extensions to a system key understood by rom_identifier / systems.* modules.
# This is intentionally a small, hand-maintained table rather than a full No-Intro/Redump
# import -- lookup_by_crc32 below is a stub extension point for wiring in a real DAT file later.
EXTENSION_TO_SYSTEM: Dict[str, str] = {
    ".smc": "snes",
    ".sfc": "snes",
    ".fig": "snes",
    ".z64": "n64",
    ".n64": "n64",
    ".v64": "n64",
    ".gba": "gba",
    ".agb": "gba",
    ".bin": "ps1",
    ".cue": "ps1",
    ".iso": "ps2",
    ".chd": "compressed_media",
    ".ciso": "compressed_media",
    ".zip": "arcade",
    ".nsp": "modern_consoles",
    ".xci": "modern_consoles",
    ".3ds": "modern_consoles",
    ".cia": "modern_consoles",
}


def system_for_extension(extension: str) -> Optional[str]:
    """Looks up the likely system key for a file extension (e.g. '.smc' -> 'snes')."""
    return EXTENSION_TO_SYSTEM.get(extension.lower())


def lookup_by_crc32(crc32: str) -> Optional[str]:
    """
    Placeholder for a real No-Intro/Redump DAT lookup keyed by CRC32.
    Always returns None until a DAT source is wired in.
    """
    return None
