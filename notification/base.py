from abc import ABC, abstractmethod

from schemas import EventIssueComment, EventPullRequest, EventPullRequestReview, GithubEventType


class NotificationProvider(ABC):
    def build_message(self, event: GithubEventType) -> str | None:
        if isinstance(event, EventPullRequest):
            return self._build_message_pull_request(event)

        if isinstance(event, EventPullRequestReview):
            return self._build_message_pull_request_review(event)

        if isinstance(event, EventIssueComment):
            return self._build_message_issue_comment(event)

    @abstractmethod
    def _build_message_pull_request(self, event: EventPullRequest) -> str | None: ...

    @abstractmethod
    def _build_message_pull_request_review(self, event: EventPullRequestReview) -> str | None: ...

    @abstractmethod
    def _build_message_issue_comment(self, event: EventIssueComment) -> str | None: ...

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
