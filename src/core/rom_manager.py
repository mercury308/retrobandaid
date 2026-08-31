import os
import tempfile
from typing import Callable, Optional

from src.core.checksum import calculate_checksums
from src.detection import rom_identifier
from src.detection.metadata import RomMetadata
from src.formats.factory import PatchFactory
from src.utils.logger import get_logger

logger = get_logger("rom_manager")


class RomManager:
    """
    Orchestrates a full patch operation: identifies the source ROM's system, strips any
    console-specific header, applies the patch via PatchFactory, then restores the header.
    """

    def apply_patch(
        self,
        source_path: str,
        patch_path: str,
        output_path: str,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> RomMetadata:
        metadata = rom_identifier.identify(source_path)
        system_module = rom_identifier.SYSTEM_MODULES.get(metadata.system) if metadata.system else None

        if metadata.system == "modern_consoles":
            from src.systems.modern_consoles import identify_container, raise_unsupported

            with open(source_path, "rb") as f:
                container = identify_container(f.read(4), metadata.extension)
            raise_unsupported(container or "modern-console")

        with open(source_path, "rb") as f:
            source_data = f.read()

        header = b""
        if system_module:
            source_data, header = system_module.strip_header(source_data)
            if header:
                logger.info(f"Stripped {len(header)}-byte header for system '{metadata.system}'")

        with tempfile.TemporaryDirectory(prefix="retrobandaid_") as tmp_dir:
            tmp_source = os.path.join(tmp_dir, "source.bin")
            tmp_output = os.path.join(tmp_dir, "output.bin")

            with open(tmp_source, "wb") as f:
                f.write(source_data)

            patcher = PatchFactory.get_patcher(tmp_source, patch_path, tmp_output)
            patcher.apply_patch(progress_callback=progress_callback)

            with open(tmp_output, "rb") as f:
                patched_data = f.read()

        if system_module:
            patched_data = system_module.restore_header(patched_data, header)

        with open(output_path, "wb") as f:
            f.write(patched_data)

        logger.info(f"Wrote patched ROM to '{output_path}'")
        return metadata

    def identify(self, file_path: str) -> RomMetadata:
        """Convenience passthrough to rom_identifier.identify()."""
        return rom_identifier.identify(file_path)

    def calculate_checksums(self, file_path: str):
        """Convenience passthrough to checksum.calculate_checksums()."""
        return calculate_checksums(file_path)
