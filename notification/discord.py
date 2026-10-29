from typing import override

import httpx

from const import GitHubAction, GitHubReviewState
from notification.base import NotificationProvider
from schemas import EventIssueComment, EventPullRequest, EventPullRequestReview, PullRequest, Sender


class DiscordNotification(NotificationProvider):
    def __init__(self, discord_webhook_url: str) -> None:
        self._discord_webhook_url = discord_webhook_url

    @staticmethod
    def _build_sender_message(sender: Sender) -> str:
        return f"[{sender.get_display_name()}]({sender.html_url})"

    @staticmethod
    def _build_pull_request_message(pull_request: PullRequest) -> str:
        return f"[PR#{pull_request.number} - {pull_request.title}]({pull_request.html_url})"

    @override
    def _build_message_pull_request(self, event: EventPullRequest) -> str | None:
        sender_msg = self._build_sender_message(event.sender)
        pr_msg = self._build_pull_request_message(event.pull_request)

        if event.action == GitHubAction.OPENED:
            return f"🆕  {sender_msg} opened {pr_msg}"

        if event.action == GitHubAction.CLOSED and event.pull_request.merged is True:
            return f"🎉  {sender_msg} merged {pr_msg}"

        if event.action == GitHubAction.CLOSED and event.pull_request.merged is False:
            return f"🔒  {sender_msg} closed {pr_msg}"

    @override
    def _build_message_pull_request_review(self, event: EventPullRequestReview) -> str | None:
        if event.action != GitHubAction.SUBMITTED:
            return

        review = event.review
        sender_msg = self._build_sender_message(event.sender)
        pr_msg = self._build_pull_request_message(event.pull_request)

        if review.state == GitHubReviewState.APPROVED:
            return f"✅  {sender_msg} [approved]({review.html_url}) {pr_msg}"

        if review.state == GitHubReviewState.CHANGES_REQUESTED:
            return f"🔄  {sender_msg} [requested changes]({review.html_url}) on {pr_msg}"

        if GitHubReviewState.COMMENTED:
            return f"💬  {sender_msg} [commented]({review.html_url}) on {pr_msg}"

    @override
    def _build_message_issue_comment(self, event: EventIssueComment) -> str | None:
        if event.pull_request is None:
            return

        sender_msg = self._build_sender_message(event.sender)
        pr_msg = self._build_pull_request_message(event.pull_request)
        return f"💬  {sender_msg} [commented]({event.comment.html_url}) on {pr_msg}"

    @override
    def send(self, message: str) -> None:
        httpx.post(self._discord_webhook_url, json={"content": message})
