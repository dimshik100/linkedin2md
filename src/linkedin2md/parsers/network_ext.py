"""Network extension section parsers.

Parsers for additional network data: groups.
"""

from linkedin2md.parsers.base import SimpleListParser
from linkedin2md.registry import register_parser


@register_parser
class GroupsParser(SimpleListParser):
    """Parse LinkedIn groups."""

    @property
    def section_key(self) -> str:
        return "groups"

    @property
    def csv_key(self) -> str:
        return "groups"

    @property
    def column_map(self) -> dict[str, str]:
        return {"Group Name": "name", "Group URL": "url"}
