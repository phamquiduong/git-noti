import logging

import httpx
from pydantic import BaseModel, ValidationError

from const import GitHubAction, GitHubReviewState

_logger = logging.getLogger(__name__)


class User(BaseModel):
    name: str


class Sender(BaseModel):
    login: str
    url: str
    html_url: str

    def get_user(self) -> User | None:
        try:
            response = httpx.get(self.url)
            response.raise_for_status()
            return User.model_validate_json(response.content)
        except (httpx.HTTPError, ValidationError):
            _logger.exception("Can not get user data: %s")

    def get_display_name(self) -> str:
        user = self.get_user()
        return user.name if user else self.login


class PullRequest(BaseModel):
    number: int
    title: str
    html_url: str
    merged: bool = False


class PullRequestReview(BaseModel):
    state: GitHubReviewState | str
    html_url: str


class IssueComment(BaseModel):
    html_url: str


class EventPullRequest(BaseModel):
    action: GitHubAction | str
    pull_request: PullRequest
    sender: Sender


class EventPullRequestReview(BaseModel):
    action: GitHubAction | str
    review: PullRequestReview
    pull_request: PullRequest
    sender: Sender


class EventIssueComment(BaseModel):
    pull_request: PullRequest | None = None
    sender: Sender
    comment: IssueComment


GithubEventType = EventPullRequest | EventPullRequestReview | EventIssueComment
