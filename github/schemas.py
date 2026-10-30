import logging

import httpx
from pydantic import BaseModel, ValidationError

from github.const import GitHubAction, GitHubReviewState, WorkFlowRunConclusion

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


class Issue(BaseModel):
    number: int
    html_url: str
    title: str


class Comment(BaseModel):
    html_url: str


class WorkFlowRun(BaseModel):
    conclusion: WorkFlowRunConclusion | str
    html_url: str
    name: str


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
    sender: Sender
    issue: Issue
    comment: Comment


class EventWorkFlowRun(BaseModel):
    action: GitHubAction | str
    workflow_run: WorkFlowRun
