import logging
from typing import override

import httpx

from notification.base import NotificationProvider

_logger = logging.getLogger(__name__)


class TelegramNotification(NotificationProvider):
    def __init__(self, bot_token: str, chat_id: str) -> None:
        self._telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        self._chat_id = chat_id

    @staticmethod
    def _build_link(display: str, url: str) -> str:
        return f'<a href="{url}">{display}</a>'

    @override
    def send(self, message: str) -> None:
        try:
            response = httpx.post(
                self._telegram_url, json={"chat_id": self._chat_id, "text": message, "parse_mode": "HTML"}
            )
            response.raise_for_status()
        except httpx.HTTPError:
            _logger.exception("Send Telegram message error")
