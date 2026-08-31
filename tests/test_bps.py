from src.formats.bps import BPSPatcher


def _write(path, data: bytes) -> str:
    path.write_bytes(data)
    return str(path)


def test_bps_source_read_and_target_read(tmp_path):
    source = b"HELLO WORLD"  # 11 bytes
    target = b"HELLO THERE"  # 11 bytes

    patch = (
        b"BPS1"
        + b"\x8B"        # source_size vint = 11
        + b"\x8B"        # target_size vint = 11
        + b"\x80"        # metadata_size vint = 0
        + bytes([((6 - 1) << 2 | 0) | 0x80])   # mode 0 (SourceRead), length 6
        + bytes([((5 - 1) << 2 | 1) | 0x80]) + b"THERE"  # mode 1 (TargetRead), length 5, literal payload
    )

    source_path = _write(tmp_path / "source.bin", source)
    patch_path = _write(tmp_path / "patch.bps", patch)
    output_path = str(tmp_path / "output.bin")

    patcher = BPSPatcher(source_path, patch_path, output_path)
    assert patcher.validate_patch() is True
    assert patcher.apply_patch() is True

    with open(output_path, "rb") as f:
        assert f.read() == target


def test_bps_target_copy_rle(tmp_path):
    """1 literal byte followed by a TargetCopy back-reference repeats it (RLE-style run)."""
    target = b"AAAAAA"  # 6 bytes, no source needed

    patch = (
        b"BPS1"
        + b"\x80"        # source_size vint = 0
        + b"\x86"        # target_size vint = 6
        + b"\x80"        # metadata_size vint = 0
        + bytes([((1 - 1) << 2 | 1) | 0x80]) + b"A"        # mode 1 (TargetRead), length 1, literal 'A'
        + bytes([((5 - 1) << 2 | 3) | 0x80]) + bytes([0 | 0x80])  # mode 3 (TargetCopy), length 5, offset delta 0
    )

    source_path = _write(tmp_path / "source.bin", b"")
    patch_path = _write(tmp_path / "patch.bps", patch)
    output_path = str(tmp_path / "output.bin")

    patcher = BPSPatcher(source_path, patch_path, output_path)
    assert patcher.apply_patch() is True

    with open(output_path, "rb") as f:
        assert f.read() == target
