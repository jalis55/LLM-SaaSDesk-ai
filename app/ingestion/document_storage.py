
from pathlib import Path

from app.core.config import DOCS_DIR
from app.ingestion.validator import validate_upload


class DocumentAlreadyExistsError(Exception):
    """Raised when a document filename already exists."""


class InvalidDocumentError(Exception):
    """Raised when a document fails validation."""


def save_document(
    filename: str,
    content: bytes,
    directory: Path = DOCS_DIR,
) -> Path:
    """Validate and save a document without overwriting existing files."""

    result = validate_upload(filename, content)

    if not result.is_valid:
        raise InvalidDocumentError(result.error)

    directory.mkdir(parents=True, exist_ok=True)

    # Prevent case-insensitive filename collisions.
    existing_names = {
        path.name.casefold()
        for path in directory.rglob("*")
        if path.is_file()
    }

    if filename.casefold() in existing_names:
        raise DocumentAlreadyExistsError(
            f"A document named '{filename}' already exists."
        )

    destination = directory / filename

    # Exclusive creation prevents overwriting an existing file.
    try:
        with destination.open("xb") as file:
            file.write(content)
    except FileExistsError as exc:
        raise DocumentAlreadyExistsError(
            f"A document named '{filename}' already exists."
        ) from exc
    except OSError:
        # Remove a partially written file if writing fails.
        destination.unlink(missing_ok=True)
        raise

    return destination
