"""Privacy and account section parsers.

Parsers for account/privacy data: contact settings, data export history,
deletion history, who viewed profile, LinkedIn salary,
profile for business, and profile summary.
"""

from linkedin2md.parsers.base import SimpleListParser
from linkedin2md.registry import register_parser


@register_parser
class ContactSettingsParser(SimpleListParser):
    """Parse contact settings."""

    @property
    def section_key(self) -> str:
        return "contact_settings"

    @property
    def csv_key(self) -> str:
        return "contact_settings"

    @property
    def column_map(self) -> dict[str, str]:
        return {"Setting": "setting", "Value": "value"}


@register_parser
class DataExportHistoryParser(SimpleListParser):
    """Parse data export history."""

    @property
    def section_key(self) -> str:
        return "data_export_history"

    @property
    def csv_key(self) -> str:
        return "data_export_history"

    @property
    def column_map(self) -> dict[str, str]:
        return {"Requested At": "requested_at", "Completed At": "completed_at"}


@register_parser
class DeletionHistoryParser(SimpleListParser):
    """Parse deletion history."""

    @property
    def section_key(self) -> str:
        return "deletion_history"

    @property
    def csv_key(self) -> str:
        return "deletion_history"

    @property
    def column_map(self) -> dict[str, str]:
        return {"Action": "action", "Date": "date"}


@register_parser
class WhoViewedProfileParser(SimpleListParser):
    """Parse who viewed your profile."""

    @property
    def section_key(self) -> str:
        return "who_viewed_profile"

    @property
    def csv_key(self) -> str:
        return "who_viewed_profile"

    @property
    def column_map(self) -> dict[str, str]:
        return {"Date": "date", "Viewer Name": "viewer"}


@register_parser
class LinkedInSalaryParser(SimpleListParser):
    """Parse LinkedIn salary insights."""

    @property
    def section_key(self) -> str:
        return "linkedin_salary"

    @property
    def csv_key(self) -> str:
        return "linkedin_salary"

    @property
    def column_map(self) -> dict[str, str]:
        return {"Company": "company", "Title": "title", "Salary": "salary"}


@register_parser
class ProfileForBusinessParser(SimpleListParser):
    """Parse profile for business data."""

    @property
    def section_key(self) -> str:
        return "profile_for_business"

    @property
    def csv_key(self) -> str:
        return "profile_for_business"

    @property
    def column_map(self) -> dict[str, str]:
        return {"Company Name": "company", "Title": "title"}


@register_parser
class ProfileSummaryParser(SimpleListParser):
    """Parse profile summary (extended)."""

    @property
    def section_key(self) -> str:
        return "profile_summary"

    @property
    def csv_key(self) -> str:
        return "profile_summary"

    @property
    def column_map(self) -> dict[str, str]:
        return {"Summary": "summary"}
