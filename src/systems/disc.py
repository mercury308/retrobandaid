from pathlib import Path
from typing import List, NamedTuple, Optional

SECTOR_SIZE_DATA = 2048     # Mode 1/2048 "ISO" sector, no sync/header/ECC
SECTOR_SIZE_RAW = 2352      # Raw Mode 1/2 sector, includes sync/header/ECC
SYNC_PATTERN = b"\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00"


def guess_sector_size(file_size: int) -> int:
    """Guesses whether a disc image uses raw (2352) or data-only (2048) sectors from its size."""
    if file_size % SECTOR_SIZE_RAW == 0:
        return SECTOR_SIZE_RAW
    if file_size % SECTOR_SIZE_DATA == 0:
        return SECTOR_SIZE_DATA
    return SECTOR_SIZE_DATA


def is_raw_image(data: bytes) -> bool:
    """True if the image starts with a raw-sector sync pattern."""
    return data[:12] == SYNC_PATTERN


class CueTrack(NamedTuple):
    file: str
    mode: str
    sector_size: int


def parse_cue_sheet(cue_path: str) -> List[CueTrack]:
    """Minimal CUE sheet parser returning the referenced track files and their sector mode."""
    tracks: List[CueTrack] = []
    current_file: Optional[str] = None
    cue_dir = Path(cue_path).parent

    with open(cue_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line.upper().startswith("FILE"):
                parts = line.split('"')
                current_file = str(cue_dir / parts[1]) if len(parts) >= 2 else None
            elif line.upper().startswith("TRACK") and current_file:
                parts = line.split()
                mode = parts[2] if len(parts) >= 3 else "MODE1/2352"
                sector_size = SECTOR_SIZE_RAW if "2352" in mode else SECTOR_SIZE_DATA
                tracks.append(CueTrack(file=current_file, mode=mode, sector_size=sector_size))

    return tracks
