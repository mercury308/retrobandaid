from typing import Optional, Tuple

from src.utils.header_parser import COPIER_HEADER_SIZE, has_copier_header, split_header, join_header

LOROM_HEADER_OFFSET = 0x7FC0
HIROM_HEADER_OFFSET = 0xFFC0


def has_header(data: bytes) -> bool:
    """True if `data` appears to carry a 512-byte SNES copier header (e.g. .smc)."""
    return has_copier_header(len(data), COPIER_HEADER_SIZE)


def strip_header(data: bytes) -> Tuple[bytes, bytes]:
    """Removes the copier header if present. Returns (rom_data, header_bytes)."""
    if has_header(data):
        return split_header(data, COPIER_HEADER_SIZE)
    return data, b""


def restore_header(rom_data: bytes, header: bytes) -> bytes:
    """Re-attaches a previously stripped copier header (no-op if header is empty)."""
    return join_header(header, rom_data) if header else rom_data


def _checksum_ok(data: bytes, header_offset: int) -> bool:
    """Validates the SNES internal checksum/complement pair (must XOR to 0xFFFF)."""
    checksum_addr = header_offset + 0x1E
    complement_addr = header_offset + 0x1C
    if checksum_addr + 2 > len(data) or complement_addr + 2 > len(data):
        return False
    checksum = int.from_bytes(data[checksum_addr:checksum_addr + 2], "little")
    complement = int.from_bytes(data[complement_addr:complement_addr + 2], "little")
    return (checksum ^ complement) == 0xFFFF


def detect_mapping(data: bytes) -> Optional[str]:
    """Returns 'lorom' or 'hirom' based on the internal header checksum, or None if neither validates."""
    if _checksum_ok(data, LOROM_HEADER_OFFSET):
        return "lorom"
    if _checksum_ok(data, HIROM_HEADER_OFFSET):
        return "hirom"
    return None


def identify(data: bytes) -> bool:
    """Best-effort check that `data` (with any copier header already stripped) is a SNES ROM."""
    rom_data, _ = strip_header(data)
    return detect_mapping(rom_data) is not None
