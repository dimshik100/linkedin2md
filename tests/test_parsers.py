"""Tests for all parser modules."""

from linkedin2md.parsers.content import (
    ArticlesParser,
    CommentsParser,
    EventsParser,
    MediaParser,
    MessagesParser,
    PostsParser,
    ReactionsParser,
    RepostsParser,
    SavedItemsParser,
    ScriptParser,
    VotesParser,
)
from linkedin2md.parsers.jobs import JobDescriptionParser
from linkedin2md.parsers.professional import (
    CertificationsParser,
    EducationParser,
    ExperienceParser,
    LanguagesParser,
    ProjectsParser,
    SkillsParser,
)
from linkedin2md.parsers.profile import (
    EmailParser,
    LocationParser,
    NameParser,
    PhoneParser,
    ProfileMetaParser,
    SummaryParser,
    TitleParser,
)
from linkedin2md.protocols import BilingualText

# =============================================================================
# Profile Parsers
# =============================================================================


class TestNameParser:
    """Tests for NameParser."""

    def test_parse_full_name(self):
        """Test parsing full name."""
        parser = NameParser()
        data = {"profile": [{"First Name": "John", "Last Name": "Doe"}]}
        result = parser.parse(data)
        assert result == "John Doe"

    def test_parse_first_name_only(self):
        """Test parsing with only first name."""
        parser = NameParser()
        data = {"profile": [{"First Name": "John", "Last Name": ""}]}
        result = parser.parse(data)
        assert result == "John"

    def test_parse_empty_profile(self):
        """Test parsing with empty profile."""
        parser = NameParser()
        data = {"profile": []}
        result = parser.parse(data)
        assert result == ""

    def test_parse_missing_profile(self):
        """Test parsing with missing profile key."""
        parser = NameParser()
        data = {}
        result = parser.parse(data)
        assert result == ""

    def test_section_key(self):
        """Test section key is correct."""
        parser = NameParser()
        assert parser.section_key == "name"


class TestTitleParser:
    """Tests for TitleParser."""

    def test_parse_title(self):
        """Test parsing headline."""
        parser = TitleParser()
        data = {"profile": [{"Headline": "Software Engineer"}]}
        result = parser.parse(data)
        assert isinstance(result, BilingualText)
        assert result.en == "Software Engineer" or result.es == "Software Engineer"

    def test_parse_empty_title(self):
        """Test parsing empty headline."""
        parser = TitleParser()
        data = {"profile": [{"Headline": ""}]}
        result = parser.parse(data)
        assert result.en == "" and result.es == ""

    def test_parse_spanish_title(self):
        """Test parsing Spanish headline."""
        parser = TitleParser()
        data = {"profile": [{"Headline": "Desarrollador de Software con experiencia"}]}
        result = parser.parse(data)
        assert result.es == "Desarrollador de Software con experiencia"


class TestEmailParser:
    """Tests for EmailParser."""

    def test_parse_primary_email(self):
        """Test parsing primary email."""
        parser = EmailParser()
        data = {
            "email_addresses": [
                {"Email Address": "secondary@test.com", "Primary": "No"},
                {"Email Address": "primary@test.com", "Primary": "Yes"},
            ]
        }
        result = parser.parse(data)
        assert result == "primary@test.com"

    def test_parse_fallback_to_first(self):
        """Test fallback to first email when no primary."""
        parser = EmailParser()
        data = {
            "email_addresses": [
                {"Email Address": "first@test.com", "Primary": "No"},
                {"Email Address": "second@test.com", "Primary": "No"},
            ]
        }
        result = parser.parse(data)
        assert result == "first@test.com"

    def test_parse_no_emails(self):
        """Test parsing with no emails."""
        parser = EmailParser()
        data = {"email_addresses": []}
        result = parser.parse(data)
        assert result == ""


class TestPhoneParser:
    """Tests for PhoneParser."""

    def test_parse_phone(self):
        """Test parsing phone number."""
        parser = PhoneParser()
        data = {"phonenumbers": [{"Number": "+1-555-1234"}]}
        result = parser.parse(data)
        assert result == "+1-555-1234"

    def test_parse_no_phone(self):
        """Test parsing with no phone."""
        parser = PhoneParser()
        data = {"phonenumbers": []}
        result = parser.parse(data)
        assert result == ""


class TestLocationParser:
    """Tests for LocationParser."""

    def test_parse_geo_location(self):
        """Test parsing Geo Location field."""
        parser = LocationParser()
        data = {"profile": [{"Geo Location": "New York, USA"}]}
        result = parser.parse(data)
        assert result == "New York, USA"

    def test_parse_fallback_location(self):
        """Test fallback to Location field."""
        parser = LocationParser()
        data = {"profile": [{"Geo Location": "", "Location": "Los Angeles"}]}
        result = parser.parse(data)
        assert result == "Los Angeles"


class TestSummaryParser:
    """Tests for SummaryParser."""

    def test_parse_english_summary(self):
        """Test parsing English summary."""
        parser = SummaryParser()
        data = {
            "profile": [
                {"Summary": "Experienced software engineer with Python expertise."}
            ]
        }
        result = parser.parse(data)
        assert result.en == "Experienced software engineer with Python expertise."

    def test_parse_spanish_summary(self):
        """Test parsing Spanish summary."""
        parser = SummaryParser()
        spanish_summary = (
            "Desarrollador de software con experiencia en Python y JavaScript."
        )
        data = {"profile": [{"Summary": spanish_summary}]}
        result = parser.parse(data)
        assert result.es == spanish_summary


class TestProfileMetaParser:
    """Tests for ProfileMetaParser."""

    def test_parse_full_meta(self):
        """Test parsing full profile metadata."""
        parser = ProfileMetaParser()
        data = {
            "profile": [
                {
                    "Industry": "Technology",
                    "Twitter Handles": "[@johndoe]",
                    "Websites": "https://example.com, https://blog.example.com",
                    "Birth Date": "1990-01-01",
                }
            ],
            "registration": [{"Registered At": "2015-05-15"}],
            "connections": [{"Name": "Alice"}, {"Name": "Bob"}],
        }
        result = parser.parse(data)
        assert result["industry"] == "Technology"
        assert result["twitter"] == "@johndoe"
        assert len(result["websites"]) == 2
        assert result["connections_count"] == 2

    def test_parse_empty_meta(self):
        """Test parsing empty metadata."""
        parser = ProfileMetaParser()
        data = {"profile": [{}], "registration": [], "connections": []}
        result = parser.parse(data)
        assert result["industry"] is None
        assert result["twitter"] is None
        assert result["websites"] == []


# =============================================================================
# Professional Parsers
# =============================================================================


class TestSkillsParser:
    """Tests for SkillsParser."""

    def test_parse_skills(self):
        """Test parsing skills list."""
        parser = SkillsParser()
        data = {"skills": [{"Name": "Python"}, {"Name": "JavaScript"}, {"Name": "Go"}]}
        result = parser.parse(data)
        assert result == ["Python", "JavaScript", "Go"]

    def test_parse_deduplicate_skills(self):
        """Test deduplication of skills."""
        parser = SkillsParser()
        data = {"skills": [{"Name": "Python"}, {"Name": "python"}, {"Name": "PYTHON"}]}
        result = parser.parse(data)
        assert len(result) == 1

    def test_parse_skills_with_spanish_parenthetical(self):
        """Test handling of bilingual skill names."""
        parser = SkillsParser()
        data = {"skills": [{"Name": "Machine Learning (Aprendizaje Automático)"}]}
        result = parser.parse(data)
        assert "Aprendizaje Automático" in result[0] or "Machine Learning" in result[0]

    def test_parse_empty_skills(self):
        """Test parsing with no skills."""
        parser = SkillsParser()
        data = {"skills": []}
        result = parser.parse(data)
        assert result == []

    def test_parse_skip_empty_skill_names(self):
        """Test skipping empty skill names."""
        parser = SkillsParser()
        data = {"skills": [{"Name": ""}, {"Name": "Python"}, {"Name": "  "}]}
        result = parser.parse(data)
        assert result == ["Python"]


class TestExperienceParser:
    """Tests for ExperienceParser."""

    def test_parse_experience(self):
        """Test parsing work experience."""
        parser = ExperienceParser()
        description = "• Led team of 5 engineers\n• Increased performance by 50%"
        data = {
            "positions": [
                {
                    "Company Name": "Acme Corp",
                    "Title": "Senior Engineer",
                    "Description": description,
                    "Location": "Remote",
                    "Started On": "Jan 2020",
                    "Finished On": "Dec 2022",
                }
            ]
        }
        result = parser.parse(data)
        assert len(result) >= 1
        assert result[0]["company"] == "Acme Corp"

    def test_parse_current_position(self):
        """Test parsing current position (no end date)."""
        parser = ExperienceParser()
        data = {
            "positions": [
                {
                    "Company Name": "Current Co",
                    "Title": "Developer",
                    "Started On": "Jan 2023",
                    "Finished On": "",
                }
            ]
        }
        result = parser.parse(data)
        assert result[0]["end"] is None


class TestEducationParser:
    """Tests for EducationParser."""

    def test_parse_education(self):
        """Test parsing education."""
        parser = EducationParser()
        data = {
            "education": [
                {
                    "School Name": "MIT",
                    "Degree Name": "B.S. Computer Science",
                    "Start Date": "2010-09-01",
                    "End Date": "2014-06-01",
                    "Notes": "Graduated with honors",
                    "Activities": "ACM Club",
                }
            ]
        }
        result = parser.parse(data)
        assert len(result) >= 1
        assert result[0]["institution"] == "MIT"
        assert result[0]["start"] == "2010"
        assert result[0]["end"] == "2014"


class TestCertificationsParser:
    """Tests for CertificationsParser."""

    def test_parse_certification(self):
        """Test parsing certifications."""
        parser = CertificationsParser()
        data = {
            "certifications": [
                {
                    "Name": "AWS Solutions Architect",
                    "Authority": "Amazon",
                    "Started On": "2023-01-15",
                    "Finished On": "2026-01-15",
                    "Url": "https://aws.amazon.com/cert/123",
                    "License Number": "ABC123",
                }
            ]
        }
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0]["name"] == "AWS Solutions Architect"
        assert result[0]["issuer"] == "Amazon"
        assert result[0]["credential_id"] == "ABC123"

    def test_parse_skip_empty_certification(self):
        """Test skipping certifications without name."""
        parser = CertificationsParser()
        data = {"certifications": [{"Name": ""}, {"Name": "Valid Cert"}]}
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0]["name"] == "Valid Cert"


class TestLanguagesParser:
    """Tests for LanguagesParser."""

    def test_parse_languages(self):
        """Test parsing languages."""
        parser = LanguagesParser()
        data = {
            "languages": [
                {"Name": "English", "Proficiency": "Native"},
                {"Name": "Spanish", "Proficiency": "Professional"},
            ]
        }
        result = parser.parse(data)
        assert len(result) == 2

    def test_parse_deduplicate_languages(self):
        """Test deduplication of languages."""
        parser = LanguagesParser()
        data = {
            "languages": [
                {"Name": "English", "Proficiency": "Native"},
                {"Name": "Inglés", "Proficiency": "Nativo"},
            ]
        }
        result = parser.parse(data)
        # Should deduplicate English/Inglés
        assert len(result) == 1

    def test_parse_normalize_spanish_names(self):
        """Test normalization of Spanish language names."""
        parser = LanguagesParser()
        data = {"languages": [{"Name": "inglés", "Proficiency": "Native"}]}
        result = parser.parse(data)
        assert result[0]["name"] == "English"


class TestProjectsParser:
    """Tests for ProjectsParser."""

    def test_parse_project(self):
        """Test parsing projects."""
        parser = ProjectsParser()
        data = {
            "projects": [
                {
                    "Title": "Open Source Tool",
                    "Description": "A tool for developers",
                    "Url": "https://github.com/example/tool",
                    "Started On": "2022-01-01",
                    "Finished On": "2022-12-31",
                }
            ]
        }
        result = parser.parse(data)
        assert len(result) >= 1
        assert result[0]["title"] == "Open Source Tool"
        assert result[0]["url"] == "https://github.com/example/tool"

    def test_parse_skip_empty_project(self):
        """Test skipping projects without title."""
        parser = ProjectsParser()
        data = {"projects": [{"Title": ""}, {"Title": "Valid Project"}]}
        result = parser.parse(data)
        assert len(result) == 1


# =============================================================================
# Edge Cases
# =============================================================================


class TestParserEdgeCases:
    """Tests for edge cases across parsers."""

    def test_missing_csv_key(self):
        """Test handling of missing CSV key."""
        parser = NameParser()
        result = parser.parse({})
        assert result == ""

    def test_empty_data(self):
        """Test handling of empty data."""
        parser = SkillsParser()
        result = parser.parse({"skills": []})
        assert result == []

    def test_malformed_data(self):
        """Test handling of malformed data."""
        parser = NameParser()
        # Missing expected fields
        result = parser.parse({"profile": [{"UnexpectedField": "value"}]})
        assert result == ""

    def test_unicode_handling(self):
        """Test handling of Unicode characters."""
        parser = NameParser()
        data = {"profile": [{"First Name": "José", "Last Name": "García"}]}
        result = parser.parse(data)
        assert result == "José García"

    def test_special_characters(self):
        """Test handling of special characters."""
        parser = TitleParser()
        data = {"profile": [{"Headline": "Engineer & Architect | Tech Lead"}]}
        result = parser.parse(data)
        assert "|" in result.get("en") or "|" in result.get("es")


# =============================================================================
# Messages Parser
# =============================================================================


class TestMessagesParser:
    """Tests for MessagesParser."""

    def test_parse_single_message(self):
        """Test parsing one valid message entry returns correct dict."""
        parser = MessagesParser()
        data = {
            "messages": [
                {
                    "CONVERSATION ID": "12345",
                    "CONVERSATION TITLE": "Project Discussion",
                    "FROM": "Alice Smith",
                    "SENDER PROFILE URL": "https://linkedin.com/in/alice",
                    "TO": "Bob Jones",
                    "RECIPIENT PROFILE URLS": "https://linkedin.com/in/bob",
                    "DATE": "2023-01-15",
                    "SUBJECT": "Meeting Notes",
                    "CONTENT": "Here are the notes from our meeting.",
                    "FOLDER": "INBOX",
                }
            ]
        }
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0] == {
            "conversation_id": "12345",
            "conversation_title": "Project Discussion",
            "from_name": "Alice Smith",
            "from_url": "https://linkedin.com/in/alice",
            "to_name": "Bob Jones",
            "to_url": "https://linkedin.com/in/bob",
            "date": "2023-01-15",
            "subject": "Meeting Notes",
            "content": "Here are the notes from our meeting.",
            "folder": "INBOX",
        }

    def test_parse_empty_messages(self):
        """Test parsing empty messages list returns []."""
        parser = MessagesParser()
        data = {"messages": []}
        result = parser.parse(data)
        assert result == []

    def test_parse_missing_date_skipped(self):
        """Test that entry with empty DATE is skipped."""
        parser = MessagesParser()
        data = {
            "messages": [
                {
                    "DATE": "",
                    "FROM": "Alice",
                    "TO": "Bob",
                    "CONTENT": "Should be skipped",
                }
            ]
        }
        result = parser.parse(data)
        assert result == []

    def test_parse_multiple_messages(self):
        """Test parsing two entries returns both."""
        parser = MessagesParser()
        data = {
            "messages": [
                {
                    "DATE": "2023-01-15",
                    "FROM": "Alice",
                    "TO": "Bob",
                    "CONTENT": "First message",
                },
                {
                    "DATE": "2023-01-16",
                    "FROM": "Charlie",
                    "TO": "Dave",
                    "CONTENT": "Second message",
                },
            ]
        }
        result = parser.parse(data)
        assert len(result) == 2
        assert result[0]["from_name"] == "Alice"
        assert result[1]["from_name"] == "Charlie"


# =============================================================================
# Script Parser
# =============================================================================


class TestScriptParser:
    """Tests for ScriptParser."""

    def test_parse_single_script(self):
        """Test one valid script entry returns dict with name/date/language/content."""
        parser = ScriptParser()
        data = {
            "scripts": [
                {
                    "NAME": "Test Script",
                    "DATE": "2023-01-15",
                    "LANGUAGE": "en",
                    "CONTENT": "Script content here",
                }
            ]
        }
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0] == {
            "name": "Test Script",
            "date": "2023-01-15",
            "language": "en",
            "content": "Script content here",
        }

    def test_parse_empty(self):
        """Test empty list returns []."""
        parser = ScriptParser()
        data = {"scripts": []}
        result = parser.parse(data)
        assert result == []

    def test_parse_no_scripts_key(self):
        """Test missing 'scripts' key returns []."""
        parser = ScriptParser()
        data = {}
        result = parser.parse(data)
        assert result == []

    def test_parse_missing_fields_handled(self):
        """Test entry without DATE or CONTENT still returns entry with defaults."""
        parser = ScriptParser()
        data = {"scripts": [{"NAME": "Incomplete Script"}]}
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0]["name"] == "Incomplete Script"
        assert result[0]["date"] == ""
        assert result[0]["language"] == "en"
        assert result[0]["content"] is None

    def test_parse_multiple_scripts(self):
        """Test two entries returns both."""
        parser = ScriptParser()
        data = {
            "scripts": [
                {
                    "NAME": "Script 1",
                    "DATE": "2023-01-15",
                    "LANGUAGE": "en",
                    "CONTENT": "First content",
                },
                {
                    "NAME": "Script 2",
                    "DATE": "2023-01-16",
                    "LANGUAGE": "es",
                    "CONTENT": "Second content",
                },
            ]
        }
        result = parser.parse(data)
        assert len(result) == 2
        assert result[0]["name"] == "Script 1"
        assert result[1]["name"] == "Script 2"


# =============================================================================
# Articles Parser
# =============================================================================


class TestArticlesParser:
    """Tests for ArticlesParser."""

    def test_parse_single_article(self):
        """Test one valid entry returns correct dict with title/date/author/summary."""
        parser = ArticlesParser()
        data = {
            "articles": [
                {
                    "TITLE": "My Article",
                    "DATE": "2023-01-15",
                    "AUTHOR": "John Doe",
                    "SUMMARY": "A brief summary",
                }
            ]
        }
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0]["title"] == "My Article"
        assert result[0]["date"] == "2023-01-15"
        assert result[0]["author"] == "John Doe"
        assert result[0]["summary"] == "A brief summary"

    def test_parse_empty(self):
        """Test empty list returns []."""
        parser = ArticlesParser()
        data = {"articles": []}
        result = parser.parse(data)
        assert result == []

    def test_parse_no_articles_key(self):
        """Test missing 'articles' key returns []."""
        parser = ArticlesParser()
        data = {}
        result = parser.parse(data)
        assert result == []


# =============================================================================
# Content Parsers
# =============================================================================


class TestPostsParser:
    """Tests for PostsParser."""

    def test_parse_single_post(self) -> None:
        """Test parsing one valid post returns correct dict with all fields."""
        parser = PostsParser()
        data = {
            "shares": [
                {
                    "Date": "2023-06-15",
                    "ShareLink": "https://linkedin.com/posts/1",
                    "ShareCommentary": "Great post about Python!",
                    "SharedUrl": "https://example.com/shared",
                    "MediaUrl": "https://media.example.com/img.jpg",
                    "Visibility": "PUBLIC",
                }
            ]
        }
        result = parser.parse(data)
        assert len(result) == 1
        entry = result[0]
        assert entry["date"] == "2023-06-15"
        assert entry["url"] == "https://linkedin.com/posts/1"
        assert entry["shared_url"] == "https://example.com/shared"
        assert entry["media_url"] == "https://media.example.com/img.jpg"
        assert entry["visibility"] == "PUBLIC"

    def test_parse_empty_date_skipped(self) -> None:
        """Test entry with empty Date is skipped."""
        parser = PostsParser()
        data = {"shares": [{"Date": "", "ShareCommentary": "No date"}]}
        result = parser.parse(data)
        assert result == []

    def test_parse_empty_shares(self) -> None:
        """Test empty shares list returns []."""
        parser = PostsParser()
        assert parser.parse({"shares": []}) == []

    def test_parse_missing_key(self) -> None:
        """Test missing 'shares' key returns []."""
        parser = PostsParser()
        assert parser.parse({}) == []

    def test_parse_optional_fields_none(self) -> None:
        """Test missing optional fields default to None."""
        parser = PostsParser()
        data = {"shares": [{"Date": "2023-06-15", "ShareCommentary": ""}]}
        result = parser.parse(data)
        assert result[0]["url"] is None
        assert result[0]["shared_url"] is None
        assert result[0]["media_url"] is None
        assert result[0]["visibility"] is None

    def test_parse_multiple_posts(self) -> None:
        """Test multiple posts returned in order."""
        parser = PostsParser()
        data = {
            "shares": [
                {"Date": "2023-01-01", "ShareCommentary": "First"},
                {"Date": "2023-06-15", "ShareCommentary": "Second"},
            ]
        }
        result = parser.parse(data)
        assert len(result) == 2

    def test_parse_unicode_content(self) -> None:
        """Test unicode content creates valid BilingualText."""
        parser = PostsParser()
        data = {
            "shares": [{"Date": "2023-06-15", "ShareCommentary": "🚀 日本語の投稿"}]
        }
        result = parser.parse(data)
        assert result[0]["content"] is not None

    def test_section_key(self) -> None:
        """Test section_key returns 'posts'."""
        assert PostsParser().section_key == "posts"


class TestCommentsParser:
    """Tests for CommentsParser."""

    def test_parse_single_comment(self) -> None:
        """Test parsing one comment returns correct dict."""
        parser = CommentsParser()
        data = {
            "comments": [
                {
                    "Date": "2023-06-15",
                    "Link": "https://linkedin.com/comments/1",
                    "Message": "Interesting perspective!",
                }
            ]
        }
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0]["date"] == "2023-06-15"
        assert result[0]["url"] == "https://linkedin.com/comments/1"
        assert result[0]["message"] is not None

    def test_parse_empty_date_skipped(self) -> None:
        """Test comment with empty Date is skipped."""
        parser = CommentsParser()
        data = {"comments": [{"Date": "", "Message": "test"}]}
        assert parser.parse(data) == []

    def test_parse_empty_comments(self) -> None:
        """Test empty comments list returns []."""
        assert CommentsParser().parse({"comments": []}) == []

    def test_parse_missing_key(self) -> None:
        """Test missing 'comments' key returns []."""
        assert CommentsParser().parse({}) == []

    def test_parse_optional_url_none(self) -> None:
        """Test missing Link defaults to None."""
        parser = CommentsParser()
        data = {"comments": [{"Date": "2023-06-15", "Message": "test"}]}
        result = parser.parse(data)
        assert result[0]["url"] is None

    def test_parse_multiple_comments(self) -> None:
        """Test multiple comments returned."""
        parser = CommentsParser()
        data = {
            "comments": [
                {"Date": "2023-01-01", "Message": "First"},
                {"Date": "2023-06-15", "Message": "Second"},
            ]
        }
        assert len(parser.parse(data)) == 2

    def test_section_key(self) -> None:
        """Test section_key returns 'comments'."""
        assert CommentsParser().section_key == "comments"


class TestReactionsParser:
    """Tests for ReactionsParser."""

    def test_parse_single_reaction(self) -> None:
        """Test parsing one reaction returns correct dict."""
        parser = ReactionsParser()
        data = {
            "reactions": [
                {"Date": "2023-06-15", "Type": "LIKE", "Link": "https://example.com"}
            ]
        }
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0]["date"] == "2023-06-15"
        assert result[0]["type"] == "LIKE"
        assert result[0]["url"] == "https://example.com"

    def test_parse_empty_date_skipped(self) -> None:
        """Test reaction with empty Date is skipped."""
        parser = ReactionsParser()
        assert parser.parse({"reactions": [{"Date": "", "Type": "LIKE"}]}) == []

    def test_parse_empty_reactions(self) -> None:
        """Test empty list returns []."""
        assert ReactionsParser().parse({"reactions": []}) == []

    def test_parse_missing_key(self) -> None:
        """Test missing 'reactions' key returns []."""
        assert ReactionsParser().parse({}) == []

    def test_parse_optional_fields_none(self) -> None:
        """Test missing Type and Link default to None."""
        parser = ReactionsParser()
        data = {"reactions": [{"Date": "2023-06-15"}]}
        result = parser.parse(data)
        assert result[0]["type"] is None
        assert result[0]["url"] is None

    def test_section_key(self) -> None:
        """Test section_key returns 'reactions'."""
        assert ReactionsParser().section_key == "reactions"


class TestRepostsParser:
    """Tests for RepostsParser."""

    def test_parse_single_repost(self) -> None:
        """Test parsing one repost returns correct dict."""
        parser = RepostsParser()
        data = {
            "instantreposts": [{"Date": "2023-06-15", "Link": "https://example.com"}]
        }
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0]["date"] == "2023-06-15"
        assert result[0]["url"] == "https://example.com"

    def test_parse_empty_date_skipped(self) -> None:
        """Test repost with empty Date is skipped."""
        assert RepostsParser().parse({"instantreposts": [{"Date": ""}]}) == []

    def test_parse_empty_list(self) -> None:
        """Test empty list returns []."""
        assert RepostsParser().parse({"instantreposts": []}) == []

    def test_parse_missing_key(self) -> None:
        """Test missing key returns []."""
        assert RepostsParser().parse({}) == []

    def test_parse_url_optional(self) -> None:
        """Test missing Link defaults to None."""
        parser = RepostsParser()
        data = {"instantreposts": [{"Date": "2023-06-15"}]}
        assert parser.parse(data)[0]["url"] is None

    def test_section_key(self) -> None:
        """Test section_key returns 'reposts'."""
        assert RepostsParser().section_key == "reposts"


class TestVotesParser:
    """Tests for VotesParser."""

    def test_parse_single_vote(self) -> None:
        """Test parsing one vote returns correct dict."""
        parser = VotesParser()
        data = {
            "votes": [
                {
                    "Date": "2023-06-15",
                    "Link": "https://example.com",
                    "OptionText": "Yes",
                }
            ]
        }
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0]["date"] == "2023-06-15"
        assert result[0]["url"] == "https://example.com"
        assert result[0]["option"] == "Yes"

    def test_parse_empty_date_skipped(self) -> None:
        """Test vote with empty Date is skipped."""
        parser = VotesParser()
        assert parser.parse({"votes": [{"Date": "", "OptionText": "Yes"}]}) == []

    def test_parse_empty_votes(self) -> None:
        """Test empty list returns []."""
        assert VotesParser().parse({"votes": []}) == []

    def test_parse_missing_key(self) -> None:
        """Test missing key returns []."""
        assert VotesParser().parse({}) == []

    def test_parse_optional_fields_none(self) -> None:
        """Test missing option defaults to None."""
        parser = VotesParser()
        data = {"votes": [{"Date": "2023-06-15"}]}
        result = parser.parse(data)
        assert result[0]["option"] is None

    def test_section_key(self) -> None:
        """Test section_key returns 'votes'."""
        assert VotesParser().section_key == "votes"


class TestSavedItemsParser:
    """Tests for SavedItemsParser."""

    def test_parse_single_item(self) -> None:
        """Test parsing one saved item returns correct dict."""
        parser = SavedItemsParser()
        data = {
            "saved_items": [
                {
                    "savedItem": "https://linkedin.com/article/123",
                    "CreatedTime": "2023-01-15T10:30:00Z",
                }
            ]
        }
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0]["url"] == "https://linkedin.com/article/123"
        assert result[0]["saved_at"] == "2023-01-15T10:30:00Z"

    def test_parse_empty_url_skipped(self) -> None:
        """Test item with empty savedItem URL is skipped."""
        parser = SavedItemsParser()
        data = {"saved_items": [{"savedItem": ""}]}
        assert parser.parse(data) == []

    def test_parse_empty_list(self) -> None:
        """Test empty list returns []."""
        assert SavedItemsParser().parse({"saved_items": []}) == []

    def test_parse_missing_key(self) -> None:
        """Test missing key returns []."""
        assert SavedItemsParser().parse({}) == []

    def test_parse_saved_at_optional(self) -> None:
        """Test missing CreatedTime defaults to None."""
        parser = SavedItemsParser()
        data = {"saved_items": [{"savedItem": "https://example.com"}]}
        assert parser.parse(data)[0]["saved_at"] is None

    def test_section_key(self) -> None:
        """Test section_key returns 'saved_items'."""
        assert SavedItemsParser().section_key == "saved_items"


class TestEventsParser:
    """Tests for EventsParser."""

    def test_parse_single_event(self) -> None:
        """Test parsing one event returns correct dict."""
        parser = EventsParser()
        data = {
            "events": [
                {
                    "Event Name": "Tech Conference 2023",
                    "Event Time": "2023-07-01T09:00:00Z",
                    "Status": "ATTENDED",
                    "External Url": "https://conf.example.com",
                }
            ]
        }
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0]["name"] == "Tech Conference 2023"
        assert result[0]["time"] == "2023-07-01T09:00:00Z"
        assert result[0]["status"] == "ATTENDED"
        assert result[0]["url"] == "https://conf.example.com"

    def test_parse_empty_name_skipped(self) -> None:
        """Test event with empty Event Name is skipped."""
        parser = EventsParser()
        assert parser.parse({"events": [{"Event Name": ""}]}) == []

    def test_parse_empty_events(self) -> None:
        """Test empty list returns []."""
        assert EventsParser().parse({"events": []}) == []

    def test_parse_missing_key(self) -> None:
        """Test missing key returns []."""
        assert EventsParser().parse({}) == []

    def test_parse_optional_fields_none(self) -> None:
        """Test missing optional fields default to None."""
        parser = EventsParser()
        data = {"events": [{"Event Name": "Minimal Event"}]}
        result = parser.parse(data)
        assert result[0]["time"] is None
        assert result[0]["status"] is None
        assert result[0]["url"] is None

    def test_parse_unicode_name(self) -> None:
        """Test unicode event name handled correctly."""
        parser = EventsParser()
        data = {"events": [{"Event Name": "Conferencia 日本語"}]}
        result = parser.parse(data)
        assert result[0]["name"] == "Conferencia 日本語"

    def test_section_key(self) -> None:
        """Test section_key returns 'events'."""
        assert EventsParser().section_key == "events"


class TestMediaParser:
    """Tests for MediaParser."""

    def test_parse_single_media(self) -> None:
        """Test parsing one media entry returns correct dict."""
        parser = MediaParser()
        data = {
            "rich_media": [
                {
                    "Media Link": "https://media.example.com/img.jpg",
                    "Date/Time": "2023-06-15T14:30:00Z",
                    "Media Description": "Team photo",
                }
            ]
        }
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0]["url"] == "https://media.example.com/img.jpg"
        assert result[0]["date"] == "2023-06-15T14:30:00Z"
        assert result[0]["description"] == "Team photo"

    def test_parse_empty_url_skipped(self) -> None:
        """Test media with empty Media Link is skipped."""
        parser = MediaParser()
        assert parser.parse({"rich_media": [{"Media Link": ""}]}) == []

    def test_parse_empty_list(self) -> None:
        """Test empty list returns []."""
        assert MediaParser().parse({"rich_media": []}) == []

    def test_parse_missing_key(self) -> None:
        """Test missing key returns []."""
        assert MediaParser().parse({}) == []

    def test_parse_optional_fields_none(self) -> None:
        """Test missing date/description default to None."""
        parser = MediaParser()
        data = {"rich_media": [{"Media Link": "https://example.com/img.jpg"}]}
        result = parser.parse(data)
        assert result[0]["date"] is None
        assert result[0]["description"] is None

    def test_section_key(self) -> None:
        """Test section_key returns 'media'."""
        assert MediaParser().section_key == "media"


class TestJobDescriptionParser:
    """Tests for JobDescriptionParser."""

    def test_parse_single_job_description(self):
        """Test parsing one valid job description entry returns correct dict."""
        parser = JobDescriptionParser()
        data = {
            "job_descriptions": [
                {
                    "Company Name": "Acme Corp",
                    "Job Title": "Senior Engineer",
                    "Description": "Build and maintain systems.",
                    "Application Date": "2024-01-15",
                    "Status": "Applied",
                }
            ]
        }
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0]["company"] == "Acme Corp"
        assert result[0]["title"] == "Senior Engineer"
        assert result[0]["description"] == "Build and maintain systems."
        assert result[0]["date_applied"] == "2024-01-15"
        assert result[0]["status"] == "Applied"

    def test_parse_fallback_to_applications(self):
        """Test fallback to job_applications CSV when job_descriptions missing."""
        parser = JobDescriptionParser()
        data = {
            "job_applications": [
                {
                    "Company": "Beta Inc",
                    "Title": "Developer",
                    "Job Description": "Code stuff.",
                    "Date Applied": "2024-02-01",
                    "Status": "Interviewed",
                }
            ]
        }
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0]["company"] == "Beta Inc"
        assert result[0]["title"] == "Developer"

    def test_parse_empty_data_returns_empty(self):
        """Test empty or missing CSV keys return empty list."""
        parser = JobDescriptionParser()
        assert parser.parse({}) == []
        assert parser.parse({"job_descriptions": []}) == []

    def test_skip_empty_company_and_title(self):
        """Test entries with both empty company and title are skipped."""
        parser = JobDescriptionParser()
        data = {
            "job_descriptions": [
                {"Company Name": "", "Job Title": ""},
                {"Company Name": "Valid Co", "Job Title": "Valid Role"},
            ]
        }
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0]["company"] == "Valid Co"

    def test_allow_title_only_entry(self):
        """Test entry with empty company but valid title passes through."""
        parser = JobDescriptionParser()
        data = {
            "job_descriptions": [
                {"Company Name": "", "Job Title": "Ghost Role"},
            ]
        }
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0]["company"] == ""
        assert result[0]["title"] == "Ghost Role"

    def test_unicode_in_fields(self):
        """Test handling of unicode characters in company/title/description."""
        parser = JobDescriptionParser()
        data = {
            "job_descriptions": [
                {
                    "Company Name": "Café ñoño",
                    "Job Title": "Développeur",
                    "Description": "日本語の説明",
                    "Application Date": "2024-03-01",
                }
            ]
        }
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0]["company"] == "Café ñoño"
        assert result[0]["title"] == "Développeur"
        assert result[0]["description"] == "日本語の説明"

    def test_missing_optional_fields_are_none(self):
        """Test missing optional fields return None."""
        parser = JobDescriptionParser()
        data = {
            "job_descriptions": [
                {"Company Name": "Minimal Co", "Job Title": "Role"},
            ]
        }
        result = parser.parse(data)
        assert result[0]["description"] is None
        assert result[0]["date_applied"] is None
        assert result[0]["status"] is None

    def test_section_key(self):
        """Test section_key returns correct value."""
        parser = JobDescriptionParser()
        assert parser.section_key == "job_descriptions"
