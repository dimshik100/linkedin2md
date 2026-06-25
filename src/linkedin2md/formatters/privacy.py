from __future__ import annotations
"""Privacy and account section formatters.

Formatters for account/privacy data: contact settings, data export history,
deletion history, who viewed profile, LinkedIn salary,
profile for business, and profile summary.
"""

from linkedin2md.formatters.base import SimpleListFormatter
from linkedin2md.registry import register_formatter


@register_formatter
class ContactSettingsFormatter(SimpleListFormatter):
    """Format contact settings section."""

    @property
    def section_key(self) -> str:
        return "contact_settings"

    @property
    def title(self) -> str:
        return "Contact Settings"

    @property
    def headers(self) -> list[str]:
        return ["Setting", "Value"]

    @property
    def fields(self) -> list[str]:
        return ["setting", "value"]


@register_formatter
class DataExportHistoryFormatter(SimpleListFormatter):
    """Format data export history section."""

    @property
    def section_key(self) -> str:
        return "data_export_history"

    @property
    def title(self) -> str:
        return "Data Export History"

    @property
    def headers(self) -> list[str]:
        return ["Requested At", "Completed At"]

    @property
    def fields(self) -> list[str]:
        return ["requested_at", "completed_at"]


@register_formatter
class DeletionHistoryFormatter(SimpleListFormatter):
    """Format deletion history section."""

    @property
    def section_key(self) -> str:
        return "deletion_history"

    @property
    def title(self) -> str:
        return "Deletion History"

    @property
    def headers(self) -> list[str]:
        return ["Action", "Date"]

    @property
    def fields(self) -> list[str]:
        return ["action", "date"]


@register_formatter
class WhoViewedProfileFormatter(SimpleListFormatter):
    """Format who viewed your profile section."""

    @property
    def section_key(self) -> str:
        return "who_viewed_profile"

    @property
    def title(self) -> str:
        return "Who Viewed Your Profile"

    @property
    def headers(self) -> list[str]:
        return ["Date", "Viewer"]

    @property
    def fields(self) -> list[str]:
        return ["date", "viewer"]


@register_formatter
class LinkedInSalaryFormatter(SimpleListFormatter):
    """Format LinkedIn salary section."""

    @property
    def section_key(self) -> str:
        return "linkedin_salary"

    @property
    def title(self) -> str:
        return "LinkedIn Salary"

    @property
    def headers(self) -> list[str]:
        return ["Company", "Title", "Salary"]

    @property
    def fields(self) -> list[str]:
        return ["company", "title", "salary"]


@register_formatter
class ProfileForBusinessFormatter(SimpleListFormatter):
    """Format profile for business section."""

    @property
    def section_key(self) -> str:
        return "profile_for_business"

    @property
    def title(self) -> str:
        return "Profile for Business"

    @property
    def headers(self) -> list[str]:
        return ["Company", "Title"]

    @property
    def fields(self) -> list[str]:
        return ["company", "title"]


@register_formatter
class ProfileSummaryFormatter(SimpleListFormatter):
    """Format profile summary (extended) section."""

    @property
    def section_key(self) -> str:
        return "profile_summary"

    @property
    def title(self) -> str:
        return "Profile Summary"

    @property
    def headers(self) -> list[str]:
        return ["Summary"]

    @property
    def fields(self) -> list[str]:
        return ["summary"]
