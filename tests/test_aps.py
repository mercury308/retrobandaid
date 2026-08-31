from src.formats.aps import APSPatcher


def _write(path, data: bytes) -> str:
    path.write_bytes(data)
    return str(path)


def test_aps_single_record_patch(tmp_path):
    source = b"AAAAAAAAAA"  # 10 bytes

    header = b"APS1" + b"\x00" + b"\x00" * 50  # standard mode + fixed 50-byte description field
    record = b"\x02\x00\x00\x00" + b"\x03\x00" + b"BBB"  # offset=2 (4-byte LE), length=3 (2-byte LE)
    patch = header + record

    source_path = _write(tmp_path / "source.bin", source)
    patch_path = _write(tmp_path / "patch.aps", patch)
    output_path = str(tmp_path / "output.bin")

    patcher = APSPatcher(source_path, patch_path, output_path)
    assert patcher.validate_patch() is True
    assert patcher.apply_patch() is True

    with open(output_path, "rb") as f:
        assert f.read() == b"AABBBAAAAA"
