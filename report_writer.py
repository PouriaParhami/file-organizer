from pathlib import Path
from transfer_result import TransferResult


class ReportWriter:
    """Builds and writes human-readable reports for transfer results."""

    @staticmethod
    def build_text_report(result: TransferResult) -> str:
        """Convert a transfer result into a plain-text report."""
        lines = []

        lines.append("Transferred Files:")
        if result.transferred_files:
            lines.extend(result.transferred_files)
        else:
            lines.append("No transferred files.")

        lines.append("")
        lines.append("Skipped Files:")
        if result.skipped_files:
            lines.extend(result.skipped_files)
        else:
            lines.append("No skipped files.")

        lines.append("")
        lines.append("Errors:")
        if result.errors:
            lines.extend(result.errors)
        else:
            lines.append("No errors.")

        return "\n".join(lines)

    @staticmethod
    def write_text_report(result: TransferResult, report_path: Path) -> None:
        """Write the generated text report to the given file path."""
        report_content = ReportWriter.build_text_report(result)
        report_path.write_text(report_content, encoding="utf-8")
