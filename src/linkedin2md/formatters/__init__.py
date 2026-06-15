"""Section formatters package.

Each formatter handles ONE section (Single Responsibility Principle).
Formatters are registered via decorators (Open/Closed Principle).
"""

from linkedin2md.formatters.activity import (
    LoginsFormatter,
    SearchQueriesFormatter,
    SecurityChallengesFormatter,
)
from linkedin2md.formatters.advertising import (
    AdsClickedFormatter,
    AdTargetingFormatter,
    InferencesFormatter,
    LanAdsFormatter,
)
from linkedin2md.formatters.base import BaseFormatter
from linkedin2md.formatters.content import (
    ArticlesFormatter,
    CommentsFormatter,
    EventsFormatter,
    MediaFormatter,
    MessagesFormatter,
    PostsFormatter,
    ReactionsFormatter,
    RepostsFormatter,
    SavedItemsFormatter,
    ScriptFormatter,
    VotesFormatter,
)
from linkedin2md.formatters.identity import (
    IdentityAssetsFormatter,
    VerificationsFormatter,
)
from linkedin2md.formatters.jobs import (
    JobApplicationsFormatter,
    JobDescriptionFormatter,
    JobPreferencesFormatter,
    SavedJobAlertsFormatter,
    SavedJobAnswersFormatter,
    SavedJobsFormatter,
    ScreeningResponsesFormatter,
)
from linkedin2md.formatters.learning import (
    LearningFormatter,
    LearningReviewsFormatter,
)
from linkedin2md.formatters.network import (
    CompaniesFollowedFormatter,
    ConnectionsFormatter,
    ImportedContactsFormatter,
    InvitationsFormatter,
    MembersFollowedFormatter,
)
from linkedin2md.formatters.network_ext import GroupsFormatter
from linkedin2md.formatters.payments import ReceiptsFormatter
from linkedin2md.formatters.privacy import (
    ContactSettingsFormatter,
    DataExportHistoryFormatter,
    DeletionHistoryFormatter,
    LinkedInSalaryFormatter,
    ProfileForBusinessFormatter,
    ProfileSummaryFormatter,
    WhoViewedProfileFormatter,
)
from linkedin2md.formatters.professional import (
    CertificationsFormatter,
    EducationFormatter,
    ExperienceFormatter,
    LanguagesFormatter,
    ProjectsFormatter,
    SkillsFormatter,
)
from linkedin2md.formatters.profile import ProfileFormatter
from linkedin2md.formatters.profile_ext import (
    CausesFormatter,
    CoursesFormatter,
    HonorsAwardsFormatter,
    InterestsFormatter,
    OrganizationsFormatter,
    PatentsFormatter,
    PublicationsFormatter,
    TestScoresFormatter,
    VolunteerExperienceFormatter,
)
from linkedin2md.formatters.recommendations import (
    EndorsementsFormatter,
    EndorsementsGivenFormatter,
    RecommendationsFormatter,
    RecommendationsGivenFormatter,
)
from linkedin2md.formatters.services import (
    ServiceEngagementsFormatter,
    ServiceOpportunitiesFormatter,
)

__all__ = [
    "BaseFormatter",
    # Profile
    "ProfileFormatter",
    # Professional
    "SkillsFormatter",
    "ExperienceFormatter",
    "EducationFormatter",
    "CertificationsFormatter",
    "LanguagesFormatter",
    "ProjectsFormatter",
    # Recommendations
    "RecommendationsFormatter",
    "RecommendationsGivenFormatter",
    "EndorsementsFormatter",
    "EndorsementsGivenFormatter",
    # Learning
    "LearningFormatter",
    "LearningReviewsFormatter",
    # Network
    "ConnectionsFormatter",
    "CompaniesFollowedFormatter",
    "MembersFollowedFormatter",
    "InvitationsFormatter",
    "ImportedContactsFormatter",
    "GroupsFormatter",
    # Content
    "PostsFormatter",
    "CommentsFormatter",
    "ReactionsFormatter",
    "RepostsFormatter",
    "VotesFormatter",
    "SavedItemsFormatter",
    "EventsFormatter",
    "MediaFormatter",
    "MessagesFormatter",
    "ScriptFormatter",
    "ArticlesFormatter",
    # Jobs
    "JobDescriptionFormatter",
    "JobApplicationsFormatter",
    "SavedJobsFormatter",
    "JobPreferencesFormatter",
    "SavedJobAnswersFormatter",
    "ScreeningResponsesFormatter",
    "SavedJobAlertsFormatter",
    # Activity
    "SearchQueriesFormatter",
    "LoginsFormatter",
    "SecurityChallengesFormatter",
    # Advertising
    "AdsClickedFormatter",
    "AdTargetingFormatter",
    "LanAdsFormatter",
    "InferencesFormatter",
    # Payments
    "ReceiptsFormatter",
    # Services
    "ServiceEngagementsFormatter",
    "ServiceOpportunitiesFormatter",
    # Identity
    "VerificationsFormatter",
    "IdentityAssetsFormatter",
    # Profile Extensions
    "CausesFormatter",
    "InterestsFormatter",
    "CoursesFormatter",
    "HonorsAwardsFormatter",
    "TestScoresFormatter",
    "PatentsFormatter",
    "OrganizationsFormatter",
    "PublicationsFormatter",
    "VolunteerExperienceFormatter",
    # Privacy / Account
    "ContactSettingsFormatter",
    "DataExportHistoryFormatter",
    "DeletionHistoryFormatter",
    "WhoViewedProfileFormatter",
    "LinkedInSalaryFormatter",
    "ProfileForBusinessFormatter",
    "ProfileSummaryFormatter",
]
