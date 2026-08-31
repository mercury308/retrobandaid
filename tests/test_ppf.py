from src.formats.ppf import PPFPatcher


def _write(path, data: bytes) -> str:
    path.write_bytes(data)
    return str(path)


def test_ppf2_single_record_patch(tmp_path):
    source = b"AAAAAAAAAA"  # 10 bytes

    header = b"PPF" + b"2" + b"\x00" * 56  # pad up to the offset-60 record start used for v2/v3
    record = b"\x02\x00\x00\x00" + b"\x03" + b"BBB"  # offset=2 (4-byte LE), length=3, payload
    patch = header + record

    source_path = _write(tmp_path / "source.bin", source)
    patch_path = _write(tmp_path / "patch.ppf", patch)
    output_path = str(tmp_path / "output.bin")

    patcher = PPFPatcher(source_path, patch_path, output_path)
    assert patcher.validate_patch() is True
    assert patcher.apply_patch() is True

    with open(output_path, "rb") as f:
        assert f.read() == b"AABBBAAAAA"
