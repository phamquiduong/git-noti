import logging
from typing import override

import httpx

from notification.base import NotificationProvider
from schemas import Comment, Issue, PullRequest, PullRequestReview, Sender

_logger = logging.getLogger(__name__)


class DiscordNotification(NotificationProvider):
    def __init__(self, discord_webhook_url: str) -> None:
        self._discord_webhook_url = discord_webhook_url

    @staticmethod
    def _build_sender_message(sender: Sender) -> str:
        return f"[{sender.get_display_name()}]({sender.html_url})"

    @staticmethod
    def _build_pull_request_message(pull_request: PullRequest) -> str:
        return f"[PR#{pull_request.number} - {pull_request.title}]({pull_request.html_url})"

    @staticmethod
    def _build_issue_message(issue: Issue) -> str:
        return f"[PR#{issue.number} - {issue.title}]({issue.html_url})"

    @staticmethod
    def _build_review_message(action: str, review: PullRequestReview) -> str:
        return f"[{action}]({review.html_url})"

    @staticmethod
    def _build_comment_message(comment: Comment) -> str:
        return f"[commented]({comment.html_url})"

    @override
    def send(self, message: str) -> None:
        try:
            response = httpx.post(self._discord_webhook_url, json={"content": message})
            response.raise_for_status()
        except httpx.HTTPError:
            _logger.exception("Send discord message error")
