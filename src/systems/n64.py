from typing import Tuple

MAGIC_Z64 = bytes([0x80, 0x37, 0x12, 0x40])  # big-endian, native
MAGIC_V64 = bytes([0x37, 0x80, 0x40, 0x12])  # byte-swapped
MAGIC_N64 = bytes([0x40, 0x12, 0x37, 0x80])  # word-swapped (little-endian)

_FORMATS = {
    b"z64": MAGIC_Z64,
    b"v64": MAGIC_V64,
    b"n64": MAGIC_N64,
}


def detect_format(data: bytes) -> str:
    """Returns 'z64', 'v64', 'n64', or 'unknown' based on the first 4 header bytes."""
    magic = data[:4]
    for name, sig in _FORMATS.items():
        if magic == sig:
            return name.decode()
    return "unknown"


def _swap16(data: bytes) -> bytes:
    """Swaps each adjacent pair of bytes (used for .v64 <-> .z64 conversion)."""
    b = bytearray(data)
    b[0::2], b[1::2] = b[1::2], b[0::2]
    return bytes(b)


def _swap32(data: bytes) -> bytes:
    """Swaps bytes within each 4-byte word (used for .n64 <-> .z64 conversion)."""
    b = bytearray(data)
    b[0::4], b[1::4], b[2::4], b[3::4] = b[3::4], b[2::4], b[1::4], b[0::4]
    return bytes(b)


def to_big_endian(data: bytes) -> Tuple[bytes, str]:
    """Normalizes any byte order to big-endian (.z64). Returns (normalized_data, original_format)."""
    fmt = detect_format(data)
    if fmt == "v64":
        return _swap16(data), fmt
    if fmt == "n64":
        return _swap32(data), fmt
    return data, fmt


def from_big_endian(data: bytes, fmt: str) -> bytes:
    """Converts big-endian (.z64) data back into the requested on-disk byte order."""
    if fmt == "v64":
        return _swap16(data)
    if fmt == "n64":
        return _swap32(data)
    return data


def has_header(data: bytes) -> bool:
    """N64 cartridge dumps don't carry a prepended copier header, only byte-order variants."""
    return False


def strip_header(data: bytes) -> Tuple[bytes, bytes]:
    """Normalizes to big-endian for patching. The 'header' is the original format name, used to restore it."""
    normalized, fmt = to_big_endian(data)
    return normalized, fmt.encode()


def restore_header(rom_data: bytes, header: bytes) -> bytes:
    """Converts big-endian data back to the original on-disk byte order."""
    fmt = header.decode() if header else "z64"
    return from_big_endian(rom_data, fmt)


def identify(data: bytes) -> bool:
    """True if `data` matches one of the three known N64 byte orders."""
    return detect_format(data) != "unknown"
