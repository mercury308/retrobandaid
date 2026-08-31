from src.core.checksum import calculate_checksums


def test_calculate_checksums(tmp_path):
    path = tmp_path / "data.bin"
    path.write_bytes(b"hello world")

    result = calculate_checksums(str(path))

    assert result["crc32"] == "0d4a1185"
    assert result["md5"] == "5eb63bbbe01eeed093cb22bb8f5acdc3"
    assert result["sha256"] == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
