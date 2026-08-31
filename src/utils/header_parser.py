from typing import Tuple

COPIER_HEADER_SIZE = 512


def split_header(data: bytes, header_size: int) -> Tuple[bytes, bytes]:
    """Splits raw data into (header, remainder) for the given header size."""
    return data[:header_size], data[header_size:]


def join_header(header: bytes, data: bytes) -> bytes:
    """Reassembles data previously split with split_header."""
    return header + data


def has_copier_header(file_size: int, header_size: int = COPIER_HEADER_SIZE) -> bool:
    """
    Heuristic used by SNES/N64-style copier headers: a headered dump's size
    is `header_size` bytes larger than a power-of-two-aligned ROM size.
    """
    if file_size <= header_size:
        return False
    unheadered_size = file_size - header_size
    return _is_rom_size_aligned(unheadered_size) and not _is_rom_size_aligned(file_size)


def _is_rom_size_aligned(size: int, block: int = 0x2000) -> bool:
    """True if size is a multiple of `block` bytes (8KB by default)."""
    return size > 0 and size % block == 0


def read_magic(data: bytes, offset: int, length: int) -> bytes:
    """Safely reads `length` bytes at `offset`, returning fewer/empty bytes if out of range."""
    return data[offset:offset + length]
