"""Main converter orchestrator with dependency injection.

Implements the Dependency Inversion Principle:
- Depends on abstractions (protocols), not concretions
- All dependencies are injected, not created internally
"""

import logging
from pathlib import Path
from typing import Any

from linkedin2md.protocols import (
    DataExtractor,
    FormatterRegistry,
    OutputWriter,
    ParserRegistry,
)

logger = logging.getLogger(__name__)


class _TrackingDict(dict):
    """Dict subclass that records which keys are accessed via get().

    Used to detect CSV files in the export that no parser consumed.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.accessed_keys: set[str] = set()

    def get(self, key: str, default: Any = None) -> Any:  # type: ignore[override]
        self.accessed_keys.add(key)
        return super().get(key, default)


class LinkedInToMarkdownConverter:
    """Main orchestrator for LinkedIn to Markdown conversion.

    SOLID Principles:
    - Single Responsibility: Only orchestrates the conversion process
    - Open/Closed: New parsers/formatters added via registries
    - Dependency Inversion: Depends on protocols, not implementations

    All dependencies are injected via constructor.
    """

    def __init__(
        self,
        extractor: DataExtractor,
        parser_registry: ParserRegistry,
        formatter_registry: FormatterRegistry,
        writer: OutputWriter,
    ):
        """Initialize with injected dependencies.

        Args:
            extractor: Extracts raw data from source
            parser_registry: Registry of section parsers
            formatter_registry: Registry of section formatters
            writer: Writes formatted output
        """
        self._extractor = extractor
        self._parsers = parser_registry
        self._formatters = formatter_registry
        self._writer = writer

    def convert(self, lang: str = "en") -> list[Path]:
        """Convert LinkedIn export to Markdown files.

        Args:
            lang: Output language ('en' or 'es')

        Returns:
            List of paths to created files
        """
        # Step 1: Extract raw CSV data
        raw_data = self._extractor.extract()

        # Step 2: Parse all sections (with key access tracking)
        tracked = _TrackingDict(raw_data)
        parsed_data = self._parse_all(tracked)

        # Step 2b: Warn about unconsumed CSV files
        all_keys = set(raw_data.keys())
        unconsumed = all_keys - tracked.accessed_keys
        for key in sorted(unconsumed):
            logger.warning("No parser consumed CSV key: %s", key)

        # Step 3: Format and write all sections
        return self._format_and_write_all(parsed_data, lang)

    def _parse_all(self, raw_data: dict[str, list[dict]]) -> dict[str, object]:
        """Parse all sections using registered parsers."""
        parsed: dict[str, object] = {}

        for parser in self._parsers.get_all():
            try:
                result = parser.parse(raw_data)
                parsed[parser.section_key] = result
            except Exception as e:
                logger.warning("Failed to parse %s: %s", parser.section_key, e)

        # Compose profile section from individual profile parsers
        parsed["profile"] = {
            "name": parsed.get("name", ""),
            "title": parsed.get("title"),
            "location": parsed.get("location", ""),
            "email": parsed.get("email", ""),
            "phone": parsed.get("phone", ""),
            "summary": parsed.get("summary"),
            "profile_meta": parsed.get("profile_meta", {}),
        }

        return parsed

    def _format_and_write_all(self, data: dict[str, object], lang: str) -> list[Path]:
        """Format and write all sections."""
        files: list[Path] = []

        for formatter in self._formatters.get_all():
            section_data = data.get(formatter.section_key)
            if not section_data:
                continue

            try:
                content = formatter.format(section_data, lang)
                if content and content.strip():
                    path = self._writer.write(formatter.section_key, content)
                    files.append(path)
            except Exception as e:
                logger.warning("Failed to format %s: %s", formatter.section_key, e)

        return files


def create_converter(
    source: Path,
    output_dir: Path,
) -> LinkedInToMarkdownConverter:
    """Factory function to create a converter with default dependencies.

    This provides a convenient way to create a fully configured converter
    while still allowing dependency injection for testing.
    """
    # Import parsers and formatters to trigger decorator registration.
    # instantiate_all() must be called after to create instances.
    from linkedin2md import (  # noqa: F401
        formatters,
        parsers,
    )
    from linkedin2md.extractor import ZipDataExtractor
    from linkedin2md.registry import get_formatter_registry, get_parser_registry
    from linkedin2md.writer import MarkdownFileWriter

    parser_registry = get_parser_registry()
    formatter_registry = get_formatter_registry()

    # Instantiate all classes registered via decorators
    parser_registry.instantiate_all()
    formatter_registry.instantiate_all()

    return LinkedInToMarkdownConverter(
        extractor=ZipDataExtractor(source),
        parser_registry=parser_registry,
        formatter_registry=formatter_registry,
        writer=MarkdownFileWriter(output_dir),
    )
