from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class TransferPlan:
    """Describes which items to iterate and whether the transfer should move files."""

    items: Iterable[Path]
    use_move: bool
