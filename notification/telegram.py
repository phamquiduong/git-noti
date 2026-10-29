import logging
from typing import override

import httpx

from notification.base import NotificationProvider
from schemas import Comment, Issue, PullRequest, PullRequestReview, Sender

_logger = logging.getLogger(__name__)


class TelegramNotification(NotificationProvider):
    def __init__(self, bot_token: str, chat_id: str) -> None:
        self._telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        self._chat_id = chat_id

    @staticmethod
    def _build_sender_message(sender: Sender) -> str:
        return f'<a href="{sender.html_url}">{sender.get_display_name()}</a>'

    @staticmethod
    def _build_pull_request_message(pull_request: PullRequest) -> str:
        return f'<a href="{pull_request.html_url}">PR#{pull_request.number} - {pull_request.title}</a>'

    @staticmethod
    def _build_issue_message(issue: Issue) -> str:
        return f'<a href="{issue.html_url}">PR#{issue.number} - {issue.title}</a>'

    @staticmethod
    def _build_review_message(action: str, review: PullRequestReview) -> str:
        return f'<a href="{review.html_url}">{action}</a>'

    @staticmethod
    def _build_comment_message(comment: Comment) -> str:
        return f'<a href="{comment.html_url}">commented</a>'

    @override
    def send(self, message: str) -> None:
        try:
            response = httpx.post(
                self._telegram_url, json={"chat_id": self._chat_id, "text": message, "parse_mode": "HTML"}
            )
            response.raise_for_status()
        except httpx.HTTPError:
            _logger.exception("Send Telegram message error")
