from typing import Type
from src.core.patcher import Patcher
from src.formats.ips import IPSPatcher
from src.formats.bps import BPSPatcher
from src.formats.ups import UPSPatcher
from src.formats.xdelta import XDeltaPatcher
from src.formats.ppf import PPFPatcher
from src.formats.aps import APSPatcher
from src.formats.bsdiff import BSDiffPatcher
"""
Factory class to create appropriate patcher instances based on the patch file extension.
"""
class PatchFactory:
    _registry = {
        ".ips": IPSPatcher,
        ".bps": BPSPatcher,
        ".ups": UPSPatcher,
        ".xdelta": XDeltaPatcher,
        ".vcdiff": XDeltaPatcher,
        ".ppf": PPFPatcher,
        ".aps": APSPatcher,
        ".bsdiff": BSDiffPatcher,
        ".bdf": BSDiffPatcher,
    }

    @classmethod
    def get_patcher(cls, source_path: str, patch_path: str, output_path: str) -> Patcher:
        import os
        ext = os.path.splitext(patch_path)[1].lower()

        patcher_class = cls._registry.get(ext)
        if not patcher_class:
            raise ValueError(f"Unsupported patch extension: '{ext}'")

        patcher = patcher_class(source_path, patch_path, output_path)
        if not patcher.validate_patch():
            raise ValueError(f"Patch validation failed for '{patch_path}'. File may be corrupt or misnamed.")

        return patcher