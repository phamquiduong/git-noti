from enum import StrEnum


class GitHubEvent(StrEnum):
    PULL_REQUEST = "pull_request"
    PULL_REQUEST_REVIEW = "pull_request_review"
    ISSUE_COMMENT = "issue_comment"


class GitHubAction(StrEnum):
    OPENED = "opened"
    CLOSED = "closed"
    SUBMITTED = "submitted"
    CREATED = "created"


class GitHubReviewState(StrEnum):
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    COMMENTED = "commented"


class NotificationMessage(StrEnum):
    PR_OPENED = "🆕 {user} opened PR#{number} - {title}\nLink PR: {url}"
    PR_MERGED = "🎉 {user} merged PR#{number} - {title}\nLink PR: {url}"
    PR_CLOSED = "🔒 {user} closed PR#{number} - {title}\nLink PR: {url}"

    REVIEW_APPROVED = "✅ {user} approved PR#{number} - {title}\nLink PR: {url}"
    REVIEW_CHANGES_REQUESTED = "🔄 {user} requested changes on PR#{number} - {title}\nLink PR: {url}"
    REVIEW_COMMENTED = "💬 {user} commented on PR#{number} - {title}\nLink PR: {url}"

    PR_COMMENTED = "💬 {user} commented on PR#{number} - {title}\nLink PR: {url}"
