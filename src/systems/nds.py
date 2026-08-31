from typing import Tuple

HEADER_SIZE = 0x200
HEADER_CRC_OFFSET = 0x15E
HEADER_CRC_LENGTH = HEADER_CRC_OFFSET


def calculate_header_crc(data: bytes) -> int:
    """Returns the CRC-16/IBM checksum used by the Nintendo DS ROM header."""
    crc = 0xFFFF
    for value in data[:HEADER_CRC_LENGTH]:
        crc ^= value
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc & 0xFFFF


def has_header(data: bytes) -> bool:
    """Nintendo DS images always include a 0x200-byte cartridge header."""
    return len(data) >= HEADER_SIZE


def strip_header(data: bytes) -> Tuple[bytes, bytes]:
    """NDS patches use on-disk offsets, so no header bytes are removed."""
    return data, b""


def restore_header(rom_data: bytes, header: bytes) -> bytes:
    """Repairs the DS header checksum after a patch changes header bytes."""
    if len(rom_data) < HEADER_SIZE:
        return rom_data

    result = bytearray(rom_data)
    result[HEADER_CRC_OFFSET:HEADER_CRC_OFFSET + 2] = calculate_header_crc(result).to_bytes(2, "little")
    return bytes(result)


def identify(data: bytes) -> bool:
    """Best-effort validation of a Nintendo DS cartridge header."""
    if len(data) < HEADER_SIZE:
        return False

    arm9_offset = int.from_bytes(data[0x20:0x24], "little")
    arm9_size = int.from_bytes(data[0x2C:0x30], "little")
    return (
        data[0x12] in (0, 2, 3)
        and HEADER_SIZE <= arm9_offset < len(data)
        and 0 < arm9_size <= len(data) - arm9_offset
    )