"""Profile section formatter.

Single Responsibility: Format profile data to Markdown.
"""

from linkedin2md.formatters.base import BaseFormatter
from linkedin2md.registry import register_formatter


@register_formatter
class ProfileFormatter(BaseFormatter):
    """Format complete profile section."""

    @property
    def section_key(self) -> str:
        return "profile"

    def _format_content(self, data: dict, lang: str) -> str:
        """Format profile data from composed profile section dict."""
        lines = []

        name = data.get("name", "")
        if name:
            lines.append(f"# {name}")
            lines.append("")

        title = self._get_text(data.get("title"), lang)
        if title:
            lines.append(f"**{title}**")
            lines.append("")

        contact_parts = []
        if data.get("location"):
            contact_parts.append(data["location"])
        if data.get("email"):
            contact_parts.append(data["email"])
        if data.get("phone"):
            contact_parts.append(data["phone"])
        if contact_parts:
            lines.append(" | ".join(contact_parts))
            lines.append("")

        summary = self._get_text(data.get("summary"), lang)
        if summary:
            lines.append("## Summary")
            lines.append("")
            lines.append(summary)
            lines.append("")

        meta = data.get("profile_meta", {})
        if meta:
            detail_lines: list[str] = []
            if meta.get("industry"):
                detail_lines.append(
                    f"- **Industry:** {self._escape_table_cell(meta['industry'])}"
                )
            if meta.get("maiden_name"):
                detail_lines.append(
                    f"- **Maiden Name:** {self._escape_table_cell(meta['maiden_name'])}"
                )
            if meta.get("public_profile_url"):
                url = self._sanitize_url(meta["public_profile_url"])
                detail_lines.append(
                    f"- **Profile URL:** "
                    f"[{self._escape_table_cell(meta['public_profile_url'])}]"
                    f"({url})"
                )
            if meta.get("address"):
                detail_lines.append(
                    f"- **Address:** {self._escape_table_cell(meta['address'])}"
                )
            if meta.get("twitter"):
                detail_lines.append(
                    f"- **Twitter:** {self._escape_table_cell(meta['twitter'])}"
                )
            if meta.get("websites"):
                for site in meta["websites"]:
                    detail_lines.append(
                        f"- **Website:** {self._escape_table_cell(site)}"
                    )
            if meta.get("birth_date"):
                detail_lines.append(
                    f"- **Birth Date:** {self._escape_table_cell(meta['birth_date'])}"
                )
            if meta.get("registered_at"):
                detail_lines.append(
                    f"- **Member Since:** "
                    f"{self._escape_table_cell(meta['registered_at'])}"
                )
            if meta.get("connections_count"):
                detail_lines.append(f"- **Connections:** {meta['connections_count']}")
            if detail_lines:
                lines.append("## Profile Details")
                lines.append("")
                lines.extend(detail_lines)
                lines.append("")

        return "\n".join(lines)
