from src.formats.ups import UPSPatcher


def _write(path, data: bytes) -> str:
    path.write_bytes(data)
    return str(path)


def test_ups_single_record_patch(tmp_path):
    source = b"AAAAAAAAAA"  # 10 bytes
    # XOR 0x03 into 3 bytes at offset 2 turns 'A' (0x41) into 'B' (0x42)
    patch = (
        b"UPS1"
        + b"\x8A"                       # src_size vint = 10
        + b"\x8A"                       # dst_size vint = 10
        + b"\x82" + b"\x03\x03\x03" + b"\x00"  # record: offset delta 2, 3 XOR bytes, terminator
        + b"\x00" * 12                  # footer (CRC32 x3), not validated by this implementation
    )

    source_path = _write(tmp_path / "source.bin", source)
    patch_path = _write(tmp_path / "patch.ups", patch)
    output_path = str(tmp_path / "output.bin")

    patcher = UPSPatcher(source_path, patch_path, output_path)
    assert patcher.validate_patch() is True
    assert patcher.apply_patch() is True

    with open(output_path, "rb") as f:
        assert f.read() == b"AABBBAAAAA"
