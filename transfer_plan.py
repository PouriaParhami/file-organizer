from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class TransferPlan:
    items: Iterable[Path]
    use_move: bool