from src.formats.ips import IPSPatcher


def _write(path, data: bytes) -> str:
    path.write_bytes(data)
    return str(path)


def test_ips_literal_and_rle_patch(tmp_path):
    source = b"AAAAAAAAAA"  # 10 bytes

    patch = (
        b"PATCH"
        + b"\x00\x00\x02" + b"\x00\x03" + b"BBB"          # literal record: offset 2, len 3 -> "BBB"
        + b"\x00\x00\x0A" + b"\x00\x00" + b"\x00\x05" + b"C"  # RLE record: offset 10, 5x 'C' (extends file)
        + b"EOF"
    )

    source_path = _write(tmp_path / "source.bin", source)
    patch_path = _write(tmp_path / "patch.ips", patch)
    output_path = str(tmp_path / "output.bin")

    patcher = IPSPatcher(source_path, patch_path, output_path)
    assert patcher.validate_patch() is True
    assert patcher.apply_patch() is True

    with open(output_path, "rb") as f:
        result = f.read()

    assert result == b"AABBBAAAAA" + b"CCCCC"


def test_ips_rejects_bad_header(tmp_path):
    source_path = _write(tmp_path / "source.bin", b"AAAA")
    patch_path = _write(tmp_path / "patch.ips", b"NOTIPS")
    output_path = str(tmp_path / "output.bin")

    patcher = IPSPatcher(source_path, patch_path, output_path)
    assert patcher.validate_patch() is False
