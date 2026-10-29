import logging

from fastapi import FastAPI, Header, Request

from const import GitHubEvent
from github import GitHubWebhook
from notification.base import Notification
from notification.discord import DiscordNotification
from settings import DISCORD_WEBHOOK_URL, GITHUB_WEBHOOK_SECRET, setup_logging

setup_logging()
_logger = logging.getLogger(__name__)

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
    _logger.info("GitHub webhook received: event=%s delivery=%s", event, delivery)

    # Not process unsupported event
    try:
        event = GitHubEvent(event)
    except ValueError:
        return {"status": "bypass", "delivery": delivery}

    body = await request.body()
    webhook = GitHubWebhook(secret=GITHUB_WEBHOOK_SECRET, body=body, signature=signature, event=event)

    # Verify Github signature
    if not webhook.verify_signature():
        return {"status": "failure", "delivery": delivery}
    _logger.info("GitHub webhook verified")

    try:
        webhook_event = webhook.parse_payload()
        _logger.info("Webhook event: %s", webhook_event)
    except Exception:
        _logger.exception("Failed to parse webhook payload")
        raise

    # Send message
    _notification.send(webhook_event)
    _logger.info("Message sent")

    return {"status": "success", "delivery": delivery}
