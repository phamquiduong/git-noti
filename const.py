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
