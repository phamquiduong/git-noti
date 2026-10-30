import hashlib
import hmac

from github.const import GitHubEvent
from github.schemas import (
    EventIssueComment,
    EventPullRequest,
    EventPullRequestReview,
    EventWorkFlowRun,
    GithubEventType,
)


class GitHubWebhook:
    def __init__(self, secret: str, body: bytes, signature: str | None, event: GitHubEvent) -> None:
        self._secret = secret
        self._body = body
        self._event = event
        self._signature = signature

    def verify_signature(self) -> None:
        if not self._secret or not self._signature:
            raise ValueError("Missing webhook secret or signature")

        expected = f"sha256={hmac.new(self._secret.encode('utf-8'), self._body, hashlib.sha256).hexdigest()}"
        if not hmac.compare_digest(self._signature, expected):
            raise ValueError("Invalid webhook signature")

    def parse_payload(self) -> GithubEventType:
        if self._event == GitHubEvent.PULL_REQUEST:
            return EventPullRequest.model_validate_json(self._body)

        if self._event == GitHubEvent.PULL_REQUEST_REVIEW:
            return EventPullRequestReview.model_validate_json(self._body)

        if self._event == GitHubEvent.ISSUE_COMMENT:
            return EventIssueComment.model_validate_json(self._body)

        if self._event == GitHubEvent.WORKFLOW_RUN:
            return EventWorkFlowRun.model_validate_json(self._body)

        raise ValueError("Can not parse webhook event")
