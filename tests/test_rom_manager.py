import pytest

from src.core.rom_manager import RomManager
from src.systems.modern_consoles import UnsupportedMediaError


def test_modern_console_container_is_rejected_before_patching(tmp_path):
    source_path = tmp_path / "game.nsp"
    source_path.write_bytes(b"PFS0")

    with pytest.raises(UnsupportedMediaError, match="not supported"):
        RomManager().apply_patch(str(source_path), "unused.ips", str(tmp_path / "output.nsp"))


def test_nds_patch_repairs_header_crc(tmp_path):
    source_path = tmp_path / "game.nds"
    source_data = bytearray(0x400)
    source_data[0x12] = 0
    source_data[0x20:0x24] = (0x200).to_bytes(4, "little")
    source_data[0x2C:0x30] = (0x20).to_bytes(4, "little")
    source_path.write_bytes(source_data)

    patch_path = tmp_path / "header-change.ips"
    patch_path.write_bytes(b"PATCH" + b"\x00\x00\x00\x00\x01XEOF")
    output_path = tmp_path / "output.nds"

    metadata = RomManager().apply_patch(str(source_path), str(patch_path), str(output_path))
    output_data = output_path.read_bytes()

    assert metadata.system == "nds"
    assert output_data[0] == ord("X")
    assert output_data[0x15E:0x160] != b"\x00\x00"