"""Main converter orchestrator with dependency injection.

Implements the Dependency Inversion Principle:
- Depends on abstractions (protocols), not concretions
- All dependencies are injected, not created internally
"""

import logging
from pathlib import Path

from linkedin2md.protocols import (
    DataExtractor,
    FormatterRegistry,
    OutputWriter,
    ParserRegistry,
)

logger = logging.getLogger(__name__)


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

        # Step 2: Parse all sections
        parsed_data = self._parse_all(raw_data)

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
    # Import here to trigger registration of parsers and formatters
    from linkedin2md import (
        formatters,  # noqa: F401
        parsers,  # noqa: F401
    )
    from linkedin2md.extractor import ZipDataExtractor
    from linkedin2md.registry import get_formatter_registry, get_parser_registry
    from linkedin2md.writer import MarkdownFileWriter

    return LinkedInToMarkdownConverter(
        extractor=ZipDataExtractor(source),
        parser_registry=get_parser_registry(),
        formatter_registry=get_formatter_registry(),
        writer=MarkdownFileWriter(output_dir),
    )
