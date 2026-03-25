from enum import Enum, auto


class TransferMode(Enum):
    """Supported file transfer strategies for copy and move operations."""

    SHALLOW_COPY = auto()
    SHALLOW_MOVE = auto()
    DEEP_COPY = auto()
    DEEP_MOVE = auto()
