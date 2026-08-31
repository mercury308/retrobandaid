from typing import Tuple

FIXED_VALUE_OFFSET = 0xB2
FIXED_VALUE = 0x96
HEADER_SIZE = 0xC0


def has_header(data: bytes) -> bool:
    """GBA cartridge dumps never carry a prepended copier header."""
    return False


def strip_header(data: bytes) -> Tuple[bytes, bytes]:
    """No-op: GBA ROMs have no separable header, only a fixed in-place header region."""
    return data, b""


def restore_header(rom_data: bytes, header: bytes) -> bytes:
    """No-op counterpart to strip_header."""
    return rom_data


def identify(data: bytes) -> bool:
    """Validates the GBA header's fixed byte (0x96 at offset 0xB2) used by the BIOS boot check."""
    if len(data) < HEADER_SIZE:
        return False
    return data[FIXED_VALUE_OFFSET] == FIXED_VALUE
