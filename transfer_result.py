from dataclasses import dataclass, field


@dataclass
class TransferResult:
    """Collects transferred files, skipped files, and transfer errors."""

    transferred_files: list[str] = field(default_factory=list)
    skipped_files: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def add_transferred(self, filename: str) -> None:
        """Record a successfully transferred file."""
        self.transferred_files.append(filename)

    def add_skipped(self, filename: str) -> None:
        """Record a file that was intentionally skipped."""
        self.skipped_files.append(filename)

    def add_error(self, message: str) -> None:
        """Record an error message produced during transfer."""
        self.errors.append(message)
