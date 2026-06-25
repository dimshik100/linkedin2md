from __future__ import annotations
"""Profile extension section parsers.

Parsers for additional profile data categories: causes, interests,
courses, honors/awards, test scores, patents, organizations,
publications, and volunteer experience.
"""

from linkedin2md.parsers.base import SimpleListParser
from linkedin2md.registry import register_parser


@register_parser
class CausesParser(SimpleListParser):
    """Parse causes/interests."""

    @property
    def section_key(self) -> str:
        return "causes"

    @property
    def csv_key(self) -> str:
        return "causes"

    @property
    def column_map(self) -> dict[str, str]:
        return {"Cause Name": "name"}


@register_parser
class InterestsParser(SimpleListParser):
    """Parse professional interests."""

    @property
    def section_key(self) -> str:
        return "interests"

    @property
    def csv_key(self) -> str:
        return "interests"

    @property
    def column_map(self) -> dict[str, str]:
        return {"Interest Name": "name"}


@register_parser
class CoursesParser(SimpleListParser):
    """Parse courses taken."""

    @property
    def section_key(self) -> str:
        return "courses"

    @property
    def csv_key(self) -> str:
        return "courses"

    @property
    def column_map(self) -> dict[str, str]:
        return {"Course Name": "name", "School": "school"}


@register_parser
class HonorsAwardsParser(SimpleListParser):
    """Parse honors and awards."""

    @property
    def section_key(self) -> str:
        return "honors_awards"

    @property
    def csv_key(self) -> str:
        return "honors_awards"

    @property
    def column_map(self) -> dict[str, str]:
        return {
            "Title": "title",
            "Issuer": "issuer",
            "Date": "date",
            "Description": "description",
        }


@register_parser
class TestScoresParser(SimpleListParser):
    """Parse test scores."""

    __test__ = False  # pytest: not a test class despite Test* name

    @property
    def section_key(self) -> str:
        return "test_scores"

    @property
    def csv_key(self) -> str:
        return "test_scores"

    @property
    def column_map(self) -> dict[str, str]:
        return {"Test Name": "name", "Score": "score", "Test Date": "date"}


@register_parser
class PatentsParser(SimpleListParser):
    """Parse patents."""

    @property
    def section_key(self) -> str:
        return "patents"

    @property
    def csv_key(self) -> str:
        return "patents"

    @property
    def column_map(self) -> dict[str, str]:
        return {
            "Title": "title",
            "Status": "status",
            "Patent Number": "number",
            "Date": "date",
        }


@register_parser
class OrganizationsParser(SimpleListParser):
    """Parse organization memberships."""

    @property
    def section_key(self) -> str:
        return "organizations"

    @property
    def csv_key(self) -> str:
        return "organizations"

    @property
    def column_map(self) -> dict[str, str]:
        return {"Organization Name": "name", "Title": "title", "Date": "date"}


@register_parser
class PublicationsParser(SimpleListParser):
    """Parse publications."""

    @property
    def section_key(self) -> str:
        return "publications"

    @property
    def csv_key(self) -> str:
        return "publications"

    @property
    def column_map(self) -> dict[str, str]:
        return {
            "Title": "title",
            "Publisher": "publisher",
            "Publication Date": "date",
            "Url": "url",
        }


@register_parser
class VolunteerExperienceParser(SimpleListParser):
    """Parse volunteer experience."""

    @property
    def section_key(self) -> str:
        return "volunteer_experience"

    @property
    def csv_key(self) -> str:
        return "volunteer_experience"

    @property
    def column_map(self) -> dict[str, str]:
        return {
            "Role": "role",
            "Organization": "organization",
            "Cause": "cause",
            "Start Date": "start_date",
            "End Date": "end_date",
        }
