from enum import StrEnum


class GitHubEvent(StrEnum):
    PULL_REQUEST = "pull_request"
    PULL_REQUEST_REVIEW = "pull_request_review"
    ISSUE_COMMENT = "issue_comment"
    WORKFLOW_RUN = "workflow_run"


class GitHubAction(StrEnum):
    OPENED = "opened"
    CLOSED = "closed"
    SUBMITTED = "submitted"
    CREATED = "created"
    COMPLETED = "completed"


class GitHubReviewState(StrEnum):
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    COMMENTED = "commented"


class WorkFlowRunConclusion(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"
