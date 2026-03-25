from enum import Enum, auto


class TransferMode(Enum):
    SHALLOW_COPY = auto()
    SHALLOW_MOVE = auto()
    DEEP_COPY = auto()
    DEEP_MOVE = auto()