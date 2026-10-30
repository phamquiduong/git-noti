import logging
from typing import override

import httpx

from notification.base import NotificationProvider

_logger = logging.getLogger(__name__)


class DiscordNotification(NotificationProvider):
    def __init__(self, discord_webhook_url: str) -> None:
        self._discord_webhook_url = discord_webhook_url

    @staticmethod
    def _build_link(display: str, url: str) -> str:
        return f"[{display}]({url})"

    @override
    def send(self, message: str) -> None:
        try:
            response = httpx.post(self._discord_webhook_url, json={"content": message})
            response.raise_for_status()
        except httpx.HTTPError:
            _logger.exception("Send discord message error")
