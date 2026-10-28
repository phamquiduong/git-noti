import hashlib
import hmac
import json

import httpx
from fastapi import FastAPI, Header, HTTPException, Request

# ==================== CONFIG ====================

GITHUB_WEBHOOK_SECRET = "rikWFDZC5cYevpehVh1QtLUP0GTXYh"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1564936561559207936/xDkXVYfiyY2A-AavRTDpJl_Jbgvym1v0nBoArxGmr9AyXyg-Co_7BFcVbBM68vBfw0MW"

# =================================================

app = FastAPI(title="GitHub to Discord")


def github_user(user: dict) -> str:
    """Format a GitHub user as a profile link."""
    login = user.get("login", "unknown")
    url = user.get("html_url", f"https://github.com/{login}")
    return f"[{login}]({url})"


def pull_request_link(pr: dict) -> str:
    """Format a pull request as a Markdown link."""
    return f"[#{pr['number']} — {pr['title']}]({pr['html_url']})"


def build_message(event: str, payload: dict) -> str | None:
    """Build a Discord message from a GitHub webhook event."""
    action = payload.get("action")
    pr = payload.get("pull_request")

    if event == "pull_request" and pr:
        link = pull_request_link(pr)

        if action == "opened":
            return f"🆕 {github_user(pr['user'])} opened {link}"

        if action == "closed":
            if pr.get("merged"):
                return f"🎉 {link} was merged"
            return f"🔒 {link} was closed"

    if event == "pull_request_review" and pr:
        if action != "submitted":
            return None

        review = payload.get("review", {})
        state = review.get("state")
        user = github_user(review.get("user", payload.get("sender", {})))
        link = pull_request_link(pr)

        if state == "approved":
            return f"✅ {user} approved {link}"

        if state == "changes_requested":
            return f"🔄 {user} requested changes on {link}"

        if state == "commented":
            return f"💬 {user} commented on {link}"

    if event == "issue_comment":
        issue = payload.get("issue", {})

        # Issue comments are relevant only when attached to a PR.
        if action == "created" and issue.get("pull_request"):
            user = github_user(payload.get("comment", {}).get("user", {}))
            link = f"[#{issue['number']} — {issue['title']}]({issue['html_url']})"
            return f"💬 {user} commented on {link}"

    if event == "pull_request_review_comment" and pr and action == "created":
        user = github_user(payload.get("comment", {}).get("user", {}))
        return f"💬 {user} commented on {pull_request_link(pr)}"

    return None


async def send_to_discord(message: str) -> None:
    """Send a message to Discord."""
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
    signature: str | None = Header(
        default=None,
        alias="X-Hub-Signature-256",
    ),
    event: str | None = Header(
        default=None,
        alias="X-GitHub-Event",
    ),
):
    body = await request.body()

    # Verify the GitHub webhook signature.
    if not signature or not GITHUB_WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid signature")

    expected = (
        "sha256="
        + hmac.new(
            GITHUB_WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
    )

    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON") from exc

    message = build_message(event or "", payload)

    if message is None:
        return {"status": "ignored"}

    try:
        await send_to_discord(message)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to send Discord notification",
        ) from exc

    return {"status": "sent"}
