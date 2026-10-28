import hashlib
import hmac
import json
import logging
import time
import uuid

import httpx
from fastapi import FastAPI, Header, HTTPException, Request

# ==================== CONFIG ====================

GITHUB_WEBHOOK_SECRET = "rikWFDZC5cYevpehVh1QtLUP0GTXYh"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1564936561559207936/xDkXVYfiyY2A-AavRTDpJl_Jbgvym1v0nBoArxGmr9AyXyg-Co_7BFcVbBM68vBfw0MW"

# =================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("github-discord")

app = FastAPI(title="GitHub to Discord")


def log_request(request_id: str, message: str) -> None:
    logger.info("[%s] %s", request_id, message)


def github_user(user: dict | None) -> str:
    user = user or {}
    login = user.get("login", "unknown")
    url = user.get("html_url", f"https://github.com/{login}")
    return f"[{login}]({url})"


def pull_request_link(pr: dict) -> str:
    return f"[#{pr['number']} — {pr['title']}]({pr['html_url']})"


def build_message(event: str, payload: dict) -> str | None:
    action = payload.get("action")
    pr = payload.get("pull_request")

    if event == "pull_request" and pr:
        link = pull_request_link(pr)

        if action == "opened":
            return f"🆕 {github_user(pr.get('user'))} opened {link}"

        if action == "closed":
            if pr.get("merged"):
                return f"🎉 {link} was merged"
            return f"🔒 {link} was closed"

    if event == "pull_request_review" and pr and action == "submitted":
        review = payload.get("review") or {}
        state = review.get("state")
        user = github_user(review.get("user") or payload.get("sender"))
        link = pull_request_link(pr)

        if state == "approved":
            return f"✅ {user} approved {link}"
        if state == "changes_requested":
            return f"🔄 {user} requested changes on {link}"
        if state == "commented":
            return f"💬 {user} commented on {link}"

    if event == "issue_comment" and action == "created":
        issue = payload.get("issue") or {}
        if issue.get("pull_request"):
            comment = payload.get("comment") or {}
            link = f"[#{issue['number']} — {issue['title']}]({issue['html_url']})"
            return f"💬 {github_user(comment.get('user'))} commented on {link}"

    if event == "pull_request_review_comment" and pr and action == "created":
        comment = payload.get("comment") or {}
        return f"💬 {github_user(comment.get('user'))} commented on {pull_request_link(pr)}"

    return None


async def send_to_discord(message: str) -> None:
    async with httpx.AsyncClient(timeout=8.0) as client:
        response = await client.post(
            DISCORD_WEBHOOK_URL,
            json={
                "content": message,
                "allowed_mentions": {"parse": []},
            },
        )
        response.raise_for_status()


@app.get("/")
async def health_check():
    return {"status": "ok"}


@app.post("/webhook")
async def github_webhook(
    request: Request,
    signature: str | None = Header(default=None, alias="X-Hub-Signature-256"),
    event: str | None = Header(default=None, alias="X-GitHub-Event"),
    delivery: str | None = Header(default=None, alias="X-GitHub-Delivery"),
):
    request_id = delivery or str(uuid.uuid4())
    start = time.perf_counter()
    action = "-"

    log_request(request_id, f"Received GitHub webhook: event={event or '-'}")

    body = await request.body()

    if not GITHUB_WEBHOOK_SECRET or not signature:
        log_request(request_id, "Rejected: webhook signature or secret is missing")
        raise HTTPException(status_code=401, detail="Invalid signature")

    expected = (
        "sha256="
        + hmac.new(
            GITHUB_WEBHOOK_SECRET.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()
    )

    if not hmac.compare_digest(signature, expected):
        log_request(request_id, "Rejected: webhook signature verification failed")
        raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        payload = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        log_request(request_id, f"Rejected: invalid JSON body ({len(body)} bytes)")
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if not isinstance(payload, dict):
        log_request(request_id, "Rejected: JSON payload must be an object")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    action = payload.get("action", "-")
    log_request(request_id, f"Verified webhook: event={event or '-'} action={action}")

    message = build_message(event or "", payload)
    if message is None:
        log_request(
            request_id,
            f"Ignored: no notification configured for event={event or '-'} action={action}",
        )
        return {"status": "ignored"}

    try:
        await send_to_discord(message)
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        logger.exception(
            "[%s] Discord returned HTTP %s (event=%s action=%s)",
            request_id,
            status,
            event,
            action,
        )
        raise HTTPException(
            status_code=502, detail="Discord rejected the notification"
        ) from exc
    except httpx.HTTPError as exc:
        logger.exception(
            "[%s] Discord request failed: %s (event=%s action=%s)",
            request_id,
            type(exc).__name__,
            event,
            action,
        )
        raise HTTPException(
            status_code=502, detail="Failed to send Discord notification"
        ) from exc

    elapsed_ms = (time.perf_counter() - start) * 1000
    log_request(
        request_id,
        f"Sent to Discord: event={event or '-'} action={action} duration={elapsed_ms:.0f}ms",
    )
    return {"status": "sent"}
