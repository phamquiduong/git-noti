from abc import ABC, abstractmethod

import httpx


class _NotificationProvider(ABC):
    @abstractmethod
    def send_message(self, message: str) -> None: ...


class DiscordNotification(_NotificationProvider):
    def __init__(self, discord_webhook_url: str) -> None:
        self.discord_webhook_url = discord_webhook_url

    def send_message(self, message: str) -> None:
        response = httpx.post(
            self.discord_webhook_url,
            json={"content": message, "allowed_mentions": {"parse": []}},
            timeout=8.0,
        )
        response.raise_for_status()


class Notification:
    def __init__(self, *providers: _NotificationProvider) -> None:
        self.providers = providers

    def send_message(self, message: str) -> None:
        for provider in self.providers:
            provider.send_message(message)
