from typing import Optional, Tuple

_SIGNATURES = {
    "nsp": b"PFS0",
    "xci": b"HEAD",
    "3ds": b"NCSD",
    "cia": None,  # CIA has no fixed magic at offset 0; identified by extension only
}


class UnsupportedMediaError(Exception):
    """Raised for encrypted/signed containers that can't be safely byte-patched without dedicated tools."""


def identify_container(data: bytes, extension: Optional[str] = None) -> Optional[str]:
    """Returns 'nsp', 'xci', '3ds', or 'cia' based on magic bytes / file extension."""
    for name, magic in _SIGNATURES.items():
        if magic is not None and data[:len(magic)] == magic:
            return name
    if extension:
        ext = extension.lower().lstrip(".")
        if ext in _SIGNATURES:
            return ext
    return None


def has_header(data: bytes) -> bool:
    return False


def strip_header(data: bytes) -> Tuple[bytes, bytes]:
    return data, b""


def restore_header(rom_data: bytes, header: bytes) -> bytes:
    return rom_data


def identify(data: bytes) -> bool:
    """True for any recognized modern-console container (Switch/3DS)."""
    return identify_container(data) is not None


def raise_unsupported(container: str) -> None:
    """
    Switch (NSP/XCI) and 3DS (3DS/CIA) titles are encrypted/signed containers.
    Byte-level patching would corrupt them; use format-specific tools instead
    (e.g. hactool/NSC_Builder for Switch, ctrtool/Checkpoint for 3DS).
    """
    raise UnsupportedMediaError(
        f"'{container}' titles are encrypted containers and are not supported for direct patching."
    )
