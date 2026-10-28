import hashlib
import hmac
import json
import logging

from consts import GitHubAction, GitHubEvent, GitHubReviewState, NotificationMessage

_logger = logging.getLogger(__name__)


class GitHubWebhook:
    def __init__(self, secret: str, body: bytes, signature: str | None, event: str | None) -> None:
        self.secret = secret
        self.body = body
        self.event = event
        self.payload = json.loads(body)
        self.signature = signature
        self._verify_signature()

    ###########################################################
    #               Build message function
    ###########################################################
    def build_message(self) -> str | None:
        if self.event == GitHubEvent.PULL_REQUEST:
            return self._pull_request()

        if self.event == GitHubEvent.PULL_REQUEST_REVIEW:
            return self._pull_request_review()

        if self.event == GitHubEvent.ISSUE_COMMENT:
            return self._issue_comment()

        return None

    def _pull_request(self) -> str | None:
        pr, user, action = self.payload["pull_request"], self.payload["sender"], self.payload["action"]
        _logger.info("Action: %s", action)

        if action == GitHubAction.OPENED:
            return self._format_message(NotificationMessage.PR_OPENED, user, pr)

        if action == GitHubAction.CLOSED:
            template = NotificationMessage.PR_MERGED if pr["merged"] else NotificationMessage.PR_CLOSED
            return self._format_message(template, user, pr)

        return None

    def _pull_request_review(self) -> str | None:
        review = self.payload["review"]
        state = review["state"]
        user = review.get("user") or self.payload["sender"]
        pr = self.payload["pull_request"]
        _logger.info("State: %s", state)

        if state == GitHubReviewState.APPROVED:
            return self._format_message(NotificationMessage.REVIEW_APPROVED, user, pr)

        if state == GitHubReviewState.CHANGES_REQUESTED:
            return self._format_message(NotificationMessage.REVIEW_CHANGES_REQUESTED, user, pr)

        return None

    def _issue_comment(self) -> str | None:
        issue, comment = self.payload["issue"], self.payload["comment"]
        user = comment["user"]

        if issue.get("pull_request"):
            return self._format_message(NotificationMessage.PR_COMMENTED, user, issue)

        return None

    ###########################################################
    #                       Utils
    ###########################################################
    def _verify_signature(self) -> None:
        if not self.secret or not self.signature:
            raise ValueError("Missing webhook secret or signature")

        expected = f"sha256={hmac.new(self.secret.encode('utf-8'), self.body, hashlib.sha256).hexdigest()}"

        if not hmac.compare_digest(self.signature, expected):
            raise ValueError("Invalid webhook signature")

    @staticmethod
    def _format_message(template: NotificationMessage, user: dict, pr: dict) -> str:
        return template.format(user=user["login"], number=pr["number"], title=pr["title"], url=pr["html_url"])
