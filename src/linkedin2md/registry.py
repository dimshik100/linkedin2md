from __future__ import annotations
"""Registry implementations for Open/Closed Principle.

Allows adding new parsers and formatters without modifying existing code.
"""

from linkedin2md.protocols import (
    FormatterRegistry,
    ParserRegistry,
    SectionFormatter,
    SectionParser,
)


class DefaultParserRegistry(ParserRegistry):
    """Default implementation of parser registry.

    Stores parser classes, instantiates on demand via instantiate_all().
    """

    def __init__(self) -> None:
        self._parser_classes: list[type[SectionParser]] = []
        self._parsers: list[SectionParser] = []

    def register_class(self, cls: type[SectionParser]) -> None:
        """Register a parser class (not instance)."""
        self._parser_classes.append(cls)

    def register(self, parser: SectionParser) -> None:
        """Register a parser instance directly."""
        self._parsers.append(parser)

    def instantiate_all(self) -> None:
        """Instantiate all registered parser classes.

        Must be called after all decorators have fired (after imports).
        """
        for cls in self._parser_classes:
            self._parsers.append(cls())
        self._parser_classes.clear()

    def get_all(self) -> list[SectionParser]:
        """Get all registered parsers."""
        return list(self._parsers)


class DefaultFormatterRegistry(FormatterRegistry):
    """Default implementation of formatter registry.

    Stores formatter classes, instantiates on demand via instantiate_all().
    """

    def __init__(self) -> None:
        self._formatter_classes: list[type[SectionFormatter]] = []
        self._formatters: dict[str, SectionFormatter] = {}

    def register_class(self, cls: type[SectionFormatter]) -> None:
        """Register a formatter class (not instance)."""
        self._formatter_classes.append(cls)

    def register(self, formatter: SectionFormatter) -> None:
        """Register a formatter instance directly."""
        self._formatters[formatter.section_key] = formatter

    def instantiate_all(self) -> None:
        """Instantiate all registered formatter classes.

        Must be called after all decorators have fired (after imports).
        """
        for cls in self._formatter_classes:
            instance = cls()
            self._formatters[instance.section_key] = instance
        self._formatter_classes.clear()

    def get(self, section_key: str) -> SectionFormatter | None:
        """Get formatter for a section key."""
        return self._formatters.get(section_key)

    def get_all(self) -> list[SectionFormatter]:
        """Get all registered formatters."""
        return list(self._formatters.values())


# ============================================================================
# Decorator-based registration for convenience
# ============================================================================

# Global registries (can be replaced via dependency injection)
_parser_registry = DefaultParserRegistry()
_formatter_registry = DefaultFormatterRegistry()


def get_parser_registry() -> ParserRegistry:
    """Get the global parser registry."""
    return _parser_registry


def get_formatter_registry() -> FormatterRegistry:
    """Get the global formatter registry."""
    return _formatter_registry


def register_parser(cls: type[SectionParser]) -> type[SectionParser]:
    """Decorator to register a parser class for later instantiation."""
    _parser_registry.register_class(cls)
    return cls


def register_formatter(cls: type[SectionFormatter]) -> type[SectionFormatter]:
    """Decorator to register a formatter class for later instantiation."""
    _formatter_registry.register_class(cls)
    return cls
