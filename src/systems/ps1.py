from typing import Tuple

from src.systems.disc import SECTOR_SIZE_DATA, SECTOR_SIZE_RAW, guess_sector_size, is_raw_image

SYNC_HEADER_SIZE = 16   # 12-byte sync + 3-byte address + 1-byte mode, prefixing the 2048-byte data field
ECC_TRAILER_SIZE = SECTOR_SIZE_RAW - SYNC_HEADER_SIZE - SECTOR_SIZE_DATA  # EDC + ECC bytes


def has_header(data: bytes) -> bool:
    """True if this BIN dump uses raw 2352-byte sectors rather than plain 2048-byte data sectors."""
    return guess_sector_size(len(data)) == SECTOR_SIZE_RAW and is_raw_image(data)


def strip_header(data: bytes) -> Tuple[bytes, bytes]:
    """
    Extracts the 2048-byte data field from each raw sector for patching against ISO-style patches.
    The removed sync/address/mode/EDC/ECC bytes are kept as a sidecar so the sectors can be
    reassembled byte-for-byte. Note: EDC/ECC are NOT recomputed on restore, so if a patch changes
    sector contents, the reinserted EDC/ECC will be stale (harmless for most emulators, which do
    not strictly validate it, but not spec-correct).
    """
    if not has_header(data):
        return data, b""

    data_only = bytearray()
    sidecars = bytearray()
    for offset in range(0, len(data), SECTOR_SIZE_RAW):
        sector = data[offset:offset + SECTOR_SIZE_RAW]
        if len(sector) < SECTOR_SIZE_RAW:
            data_only.extend(sector)  # trailing partial sector, keep as-is
            continue
        sidecars.extend(sector[:SYNC_HEADER_SIZE])
        data_only.extend(sector[SYNC_HEADER_SIZE:SYNC_HEADER_SIZE + SECTOR_SIZE_DATA])
        sidecars.extend(sector[SYNC_HEADER_SIZE + SECTOR_SIZE_DATA:])

    return bytes(data_only), bytes(sidecars)


def restore_header(rom_data: bytes, header: bytes) -> bytes:
    """Reassembles raw 2352-byte sectors from stripped data using the sidecar bytes from strip_header."""
    if not header:
        return rom_data

    sidecar_per_sector = SYNC_HEADER_SIZE + ECC_TRAILER_SIZE
    raw = bytearray()
    for i, offset in enumerate(range(0, len(rom_data), SECTOR_SIZE_DATA)):
        chunk = rom_data[offset:offset + SECTOR_SIZE_DATA]
        side_offset = i * sidecar_per_sector
        sidecar = header[side_offset:side_offset + sidecar_per_sector]
        if len(chunk) < SECTOR_SIZE_DATA or len(sidecar) < sidecar_per_sector:
            raw.extend(chunk)  # trailing partial sector
            continue
        raw.extend(sidecar[:SYNC_HEADER_SIZE])
        raw.extend(chunk)
        raw.extend(sidecar[SYNC_HEADER_SIZE:])

    return bytes(raw)


def identify(data: bytes) -> bool:
    """True if `data` looks like a PS1 disc image (raw BIN or plain 2048-byte ISO)."""
    return guess_sector_size(len(data)) in (SECTOR_SIZE_RAW, SECTOR_SIZE_DATA)
