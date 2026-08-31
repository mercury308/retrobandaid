from src.systems import n64, nds, snes


def test_snes_strip_and_restore_copier_header():
    rom_body = b"\x01" * 32768  # 32KB, aligned ROM body
    headered = b"\xAA" * 512 + rom_body  # 512-byte copier header prepended

    assert snes.has_header(headered) is True
    stripped, header = snes.strip_header(headered)
    assert stripped == rom_body
    assert header == b"\xAA" * 512
    assert snes.restore_header(stripped, header) == headered


def test_snes_no_header_when_already_aligned():
    rom_body = b"\x01" * 32768
    assert snes.has_header(rom_body) is False
    stripped, header = snes.strip_header(rom_body)
    assert stripped == rom_body
    assert header == b""


def test_n64_byte_order_round_trip():
    z64_data = n64.MAGIC_Z64 + b"\x01\x02\x03\x04"
    v64_data = n64._swap16(z64_data)
    n64_data = n64._swap32(z64_data)

    assert n64.detect_format(z64_data) == "z64"
    assert n64.detect_format(v64_data) == "v64"
    assert n64.detect_format(n64_data) == "n64"

    normalized, fmt = n64.to_big_endian(v64_data)
    assert normalized == z64_data
    assert n64.from_big_endian(normalized, fmt) == v64_data


def test_nds_identifies_valid_header_and_repairs_header_crc():
    rom = bytearray(0x400)
    rom[0x12] = 0
    rom[0x20:0x24] = (0x200).to_bytes(4, "little")
    rom[0x2C:0x30] = (0x20).to_bytes(4, "little")

    assert nds.identify(rom) is True
    restored = nds.restore_header(bytes(rom), b"")
    assert int.from_bytes(restored[0x15E:0x160], "little") == nds.calculate_header_crc(restored)
