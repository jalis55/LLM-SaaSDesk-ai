
from dataclasses import dataclass
from pathlib import Path
import re


ALLOWED_EXTENSIONS = {".pdf", ".md", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MiB

SAFE_FILENAME_PATTERN = re.compile(
    r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$"
)


@dataclass
class ValidationResult:
    is_valid: bool
    error: str | None = None


def validate_upload(
    filename: str,
    content: bytes,
) -> ValidationResult:
    """Validate an uploaded document before saving."""

    if not filename:
        return ValidationResult(
            False,
            "Filename cannot be empty.",
        )

    if (
        filename in {".", ".."}
        or not SAFE_FILENAME_PATTERN.fullmatch(filename)
    ):
        return ValidationResult(
            False,
            "Filename contains unsupported characters.",
        )

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return ValidationResult(
            False,
            "Only PDF, Markdown, and TXT files are allowed.",
        )

    if not content:
        return ValidationResult(
            False,
            "The uploaded file is empty.",
        )

    if len(content) > MAX_FILE_SIZE:
        return ValidationResult(
            False,
            "File exceeds the 10 MiB size limit.",
        )

    # Basic file-content checks
    if extension == ".pdf":
        if not content.startswith(b"%PDF-"):
            return ValidationResult(
                False,
                "File does not have a valid PDF header.",
            )

    if extension in {".md", ".txt"}:
        try:
            content.decode("utf-8")
        except UnicodeDecodeError:
            return ValidationResult(
                False,
                "Text documents must use UTF-8 encoding.",
            )

    return ValidationResult(True)
