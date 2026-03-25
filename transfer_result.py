from dataclasses import dataclass, field


@dataclass
class TransferResult:
    transferred_files: list[str] = field(default_factory=list)
    skipped_files: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def add_transferred(self, filename: str) -> None:
        self.transferred_files.append(filename)

    def add_skipped(self, filename: str) -> None:
        self.skipped_files.append(filename)

    def add_error(self, message: str) -> None:
        self.errors.append(message)