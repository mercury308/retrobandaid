from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class RomMetadata:
    """Summary of a ROM/disc image gathered by rom_identifier.identify()."""
    path: str
    system: Optional[str]
    size: int
    extension: str
    has_header: bool = False
    checksums: Dict[str, str] = field(default_factory=dict)
    known_name: Optional[str] = None  # populated by database.lookup_by_crc32 when available
