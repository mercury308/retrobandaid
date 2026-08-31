from typing import Tuple

from src.systems.disc import SECTOR_SIZE_DATA, guess_sector_size

ISO9660_MAGIC = b"CD001"
ISO9660_MAGIC_OFFSET = 0x8001  # sector 16, byte 1 of a 2048-byte-sector ISO9660 image


def has_header(data: bytes) -> bool:
    """PS2 DVD images are almost always plain 2048-byte sectors with no prepended header."""
    return False


def strip_header(data: bytes) -> Tuple[bytes, bytes]:
    """No-op: PS2 ISOs are patched directly at their native byte offsets."""
    return data, b""


def restore_header(rom_data: bytes, header: bytes) -> bytes:
    """No-op counterpart to strip_header."""
    return rom_data


def identify(data: bytes) -> bool:
    """True if `data` is 2048-byte-sector aligned and carries an ISO9660 volume descriptor."""
    if guess_sector_size(len(data)) != SECTOR_SIZE_DATA:
        return False
    magic_pos = data.find(ISO9660_MAGIC, ISO9660_MAGIC_OFFSET - 8, ISO9660_MAGIC_OFFSET + 8)
    return magic_pos != -1
