import logging

from fastapi import FastAPI, Header, Request

from github import GitHubWebhook
from notification import DiscordNotification, Notification
from settings import DISCORD_WEBHOOK_URL, GITHUB_WEBHOOK_SECRET, setup_logging

setup_logging()
_logger = logging.getLogger("github-discord")

_notification = Notification(
    DiscordNotification(DISCORD_WEBHOOK_URL),
)

app = FastAPI()


@app.get("/")
async def health_check() -> dict:
    return {"status": "ok"}


@app.post("/webhook")
async def github_webhook(
    request: Request,
    signature: str | None = Header(default=None, alias="X-Hub-Signature-256"),
    event: str | None = Header(default=None, alias="X-GitHub-Event"),
    delivery: str | None = Header(default=None, alias="X-GitHub-Delivery"),
) -> dict:
    _logger.info("GitHub webhook received", extra={"event": event, "delivery": delivery})
    body = await request.body()

    webhook = GitHubWebhook(secret=GITHUB_WEBHOOK_SECRET, body=body, signature=signature, event=event)
    _logger.info("GitHub webhook verified", extra={"event": event, "delivery": delivery})

    message = webhook.build_message()

    if message:
        _logger.info("Discord notification prepared", extra={"event": event, "delivery": delivery})
        _notification.send_message(message)
        _logger.info("Discord notification sent", extra={"event": event, "delivery": delivery})

    return {"status": "success", "delivery": delivery}
