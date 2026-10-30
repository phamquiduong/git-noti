from abc import ABC, abstractmethod

from github.const import GitHubAction, GitHubEvent, GitHubReviewState, WorkFlowRunConclusion
from github.schemas import EventIssueComment, EventPullRequest, EventPullRequestReview, EventWorkFlowRun


class NotificationProvider(ABC):
    def build_message(self, event: GitHubEvent, body: bytes) -> str | None:
        if event == GitHubEvent.PULL_REQUEST:
            return self._build_message_pull_request(EventPullRequest.model_validate_json(body))

        if event == GitHubEvent.PULL_REQUEST_REVIEW:
            return self._build_message_pull_request_review(EventPullRequestReview.model_validate_json(body))

        if event == GitHubEvent.ISSUE_COMMENT:
            return self._build_message_issue_comment(EventIssueComment.model_validate_json(body))

        if event == GitHubEvent.WORKFLOW_RUN:
            return self._build_message_workflow_run(EventWorkFlowRun.model_validate_json(body))

    def _build_message_pull_request(self, event: EventPullRequest) -> str | None:
        sender, pr, action = event.sender, event.pull_request, event.action

        sender_msg = self._build_link(sender.get_display_name(), sender.html_url)
        pr_msg = self._build_link(f"PR#{pr.number} - {pr.title}", pr.html_url)

        if action == GitHubAction.OPENED:
            return f"🆕  {sender_msg} opened {pr_msg}"

        if action == GitHubAction.CLOSED and pr.merged is True:
            return f"🎉  {sender_msg} merged {pr_msg}"

        if action == GitHubAction.CLOSED and pr.merged is False:
            return f"🔒  {sender_msg} closed {pr_msg}"

    def _build_message_pull_request_review(self, event: EventPullRequestReview) -> str | None:
        if event.action != GitHubAction.SUBMITTED:
            return

        review, sender, pr = event.review, event.sender, event.pull_request

        sender_msg = self._build_link(sender.get_display_name(), sender.html_url)
        pr_msg = self._build_link(f"PR#{pr.number} - {pr.title}", pr.html_url)

        if review.state == GitHubReviewState.APPROVED:
            state = self._build_link("approved", review.html_url)
            return f"✅  {sender_msg} {state} on {pr_msg}"

        if review.state == GitHubReviewState.CHANGES_REQUESTED:
            state = self._build_link("requested changes", review.html_url)
            return f"🔄  {sender_msg} {state} on {pr_msg}"

        if review.state == GitHubReviewState.COMMENTED:
            state = self._build_link("commented", review.html_url)
            return f"💬  {sender_msg} {state} on {pr_msg}"

    def _build_message_issue_comment(self, event: EventIssueComment) -> str:
        sender, issue, comment_msg = event.sender, event.issue, event.comment

        sender_msg = self._build_link(sender.get_display_name(), sender.html_url)
        issue_msg = self._build_link(f"Issue#{issue.number} - {issue.title}", issue.html_url)
        comment_msg = self._build_link("commented", comment_msg.html_url)

        return f"💬  {sender_msg} {comment_msg} on {issue_msg}"

    def _build_message_workflow_run(self, event: EventWorkFlowRun) -> str | None:
        if event.action != GitHubAction.COMPLETED:
            return

        workflow_run = event.workflow_run
        workflow_run_msg = self._build_link(f"Workflow - {workflow_run.name}", workflow_run.html_url)

        if workflow_run.conclusion == WorkFlowRunConclusion.SUCCESS:
            return f"🚀  {workflow_run_msg} run success"

        if workflow_run.conclusion == WorkFlowRunConclusion.FAILURE:
            return f"❌  {workflow_run_msg} run failure"

    @staticmethod
    @abstractmethod
    def _build_link(display: str, url: str) -> str: ...

    @abstractmethod
    def send(self, message: str) -> None: ...


class Notification:
    def __init__(self, *providers: NotificationProvider) -> None:
        self._providers = providers

    def send(self, event: GitHubEvent, body: bytes) -> None:
        for provider in self._providers:
            message = provider.build_message(event, body)
            if message:
                provider.send(message)
