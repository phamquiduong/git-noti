import hashlib
import hmac
import logging

from github.const import GitHubEvent
from github.schemas import EventIssueComment, EventPullRequest, EventPullRequestReview, GithubEventType

_logger = logging.getLogger(__name__)


class GitHubWebhook:
    def __init__(self, secret: str, body: bytes, signature: str | None, event: GitHubEvent) -> None:
        self._secret = secret
        self._body = body
        self._event = event
        self._signature = signature

    def verify_signature(self) -> bool:
        if not self._secret or not self._signature:
            _logger.error("Missing webhook secret or signature")
            return False

        expected = f"sha256={hmac.new(self._secret.encode('utf-8'), self._body, hashlib.sha256).hexdigest()}"
        if hmac.compare_digest(self._signature, expected):
            return True

        _logger.error("Invalid webhook signature")
        return False

    def parse_payload(self) -> GithubEventType:
        if self._event == GitHubEvent.PULL_REQUEST:
            return EventPullRequest.model_validate_json(self._body)

        if self._event == GitHubEvent.PULL_REQUEST_REVIEW:
            return EventPullRequestReview.model_validate_json(self._body)

        return EventIssueComment.model_validate_json(self._body)
