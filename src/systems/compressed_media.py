import struct
import zlib
from typing import Optional, Tuple

CHD_MAGIC = b"MComprHD"
CISO_MAGIC = b"CISO"


class UnsupportedMediaError(Exception):
    """Raised when a compressed media container can't be safely patched without external tools."""


def identify_container(data: bytes) -> Optional[str]:
    """Returns 'chd', 'ciso', 'zip', or None based on magic bytes."""
    if data[:8] == CHD_MAGIC:
        return "chd"
    if data[:4] == CISO_MAGIC:
        return "ciso"
    if data[:4] == b"PK\x03\x04":
        return "zip"
    return None


def has_header(data: bytes) -> bool:
    return False


def strip_header(data: bytes) -> Tuple[bytes, bytes]:
    return data, b""


def restore_header(rom_data: bytes, header: bytes) -> bytes:
    return rom_data


def identify(data: bytes) -> bool:
    """True for any recognized compressed media container."""
    return identify_container(data) is not None


def decompress_ciso(data: bytes) -> bytes:
    """
    Decompresses a CISO (Compact ISO) image, as commonly used for PSP UMD dumps.
    Layout: 0x18-byte header, then a block index table of (num_blocks + 1) uint32 offsets,
    each with the high bit set if the block is stored uncompressed.
    """
    if data[:4] != CISO_MAGIC:
        raise ValueError("Not a CISO image (bad magic).")

    header_size, total_bytes, block_size = struct.unpack_from("<III", data, 4)
    num_blocks = total_bytes // block_size
    index_offset = header_size if header_size else 0x18

    offsets = struct.unpack_from(f"<{num_blocks + 1}I", data, index_offset)

    out = bytearray()
    for i in range(num_blocks):
        raw_offset = offsets[i]
        next_offset = offsets[i + 1]
        compressed = (raw_offset & 0x80000000) == 0
        start = raw_offset & 0x7FFFFFFF
        end = next_offset & 0x7FFFFFFF

        block = data[start:end]
        if compressed:
            block = zlib.decompress(block, -15)  # raw deflate, no zlib/gzip wrapper
        out.extend(block.ljust(block_size, b"\x00")[:block_size])

    return bytes(out)


def raise_unsupported(container: str) -> None:
    """CHD and similar compressed disc formats require external tools (e.g. chdman) to decode."""
    raise UnsupportedMediaError(
        f"'{container}' containers must be decompressed with an external tool "
        "(e.g. 'chdman extractcd') before patching; direct byte patching is not supported."
    )
