import io
import zipfile
from typing import List, Tuple


def has_header(data: bytes) -> bool:
    """Arcade ROM sets are zip archives; there is no per-file header to strip at this level."""
    return False


def strip_header(data: bytes) -> Tuple[bytes, bytes]:
    """No-op: use list_members/extract_member/replace_member to work with individual chip dumps."""
    return data, b""


def restore_header(rom_data: bytes, header: bytes) -> bytes:
    """No-op counterpart to strip_header."""
    return rom_data


def identify(data: bytes) -> bool:
    """True if `data` is a zip archive (the standard MAME ROM set container)."""
    return data[:4] == b"PK\x03\x04"


def list_members(zip_path: str) -> List[str]:
    """Lists the individual ROM chip dump filenames inside a MAME-style zip romset."""
    with zipfile.ZipFile(zip_path, "r") as zf:
        return zf.namelist()


def extract_member(zip_path: str, member_name: str) -> bytes:
    """Reads a single chip dump out of a romset zip."""
    with zipfile.ZipFile(zip_path, "r") as zf:
        return zf.read(member_name)


def replace_member(zip_path: str, member_name: str, new_data: bytes, output_zip_path: str) -> None:
    """Writes a copy of the romset zip with one member's contents replaced."""
    with zipfile.ZipFile(zip_path, "r") as src_zf:
        with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as dst_zf:
            for item in src_zf.infolist():
                data = new_data if item.filename == member_name else src_zf.read(item.filename)
                dst_zf.writestr(item, data)
