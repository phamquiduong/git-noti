from abc import ABC, abstractmethod

from const import GitHubAction, GitHubReviewState
from schemas import (
    Comment,
    EventIssueComment,
    EventPullRequest,
    EventPullRequestReview,
    GithubEventType,
    Issue,
    PullRequest,
    PullRequestReview,
    Sender,
)


class NotificationProvider(ABC):
    def build_message(self, event: GithubEventType) -> str | None:
        if isinstance(event, EventPullRequest):
            return self._build_message_pull_request(event)

        if isinstance(event, EventPullRequestReview):
            return self._build_message_pull_request_review(event)

        if isinstance(event, EventIssueComment):
            return self._build_message_issue_comment(event)

    def _build_message_pull_request(self, event: EventPullRequest) -> str | None:
        sender_msg = self._build_sender_message(event.sender)
        pr_msg = self._build_pull_request_message(event.pull_request)

        if event.action == GitHubAction.OPENED:
            return f"🆕  {sender_msg} opened {pr_msg}"

        if event.action == GitHubAction.CLOSED and event.pull_request.merged is True:
            return f"🎉  {sender_msg} merged {pr_msg}"

        if event.action == GitHubAction.CLOSED and event.pull_request.merged is False:
            return f"🔒  {sender_msg} closed {pr_msg}"

    def _build_message_pull_request_review(self, event: EventPullRequestReview) -> str | None:
        if event.action != GitHubAction.SUBMITTED:
            return

        review = event.review
        sender_msg = self._build_sender_message(event.sender)
        pr_msg = self._build_pull_request_message(event.pull_request)

        if review.state == GitHubReviewState.APPROVED:
            state_msg = self._build_review_message("approved", review)
            return f"✅  {sender_msg} {state_msg} on {pr_msg}"

        if review.state == GitHubReviewState.CHANGES_REQUESTED:
            state_msg = self._build_review_message("requested changes", review)
            return f"🔄  {sender_msg} {state_msg} on {pr_msg}"

        if GitHubReviewState.COMMENTED:
            state_msg = self._build_review_message("commented", review)
            return f"💬  {sender_msg} {state_msg} on {pr_msg}"

    def _build_message_issue_comment(self, event: EventIssueComment) -> str | None:
        sender_msg = self._build_sender_message(event.sender)
        issue_msg = self._build_issue_message(event.issue)
        comment_msg = self._build_comment_message(event.comment)
        return f"💬  {sender_msg} {comment_msg} on {issue_msg}"

    @staticmethod
    @abstractmethod
    def _build_sender_message(sender: Sender) -> str: ...

    @staticmethod
    @abstractmethod
    def _build_pull_request_message(pull_request: PullRequest) -> str: ...

    @staticmethod
    @abstractmethod
    def _build_issue_message(issue: Issue) -> str: ...

    @staticmethod
    @abstractmethod
    def _build_review_message(action: str, review: PullRequestReview) -> str: ...

    @staticmethod
    @abstractmethod
    def _build_comment_message(comment: Comment) -> str: ...

    @abstractmethod
    def send(self, message: str) -> None: ...


class Notification:
    def __init__(self, *providers: NotificationProvider) -> None:
        self._providers = providers

    def send(self, event: GithubEventType) -> None:
        for provider in self._providers:
            message = provider.build_message(event)
            if message:
                provider.send(message)
