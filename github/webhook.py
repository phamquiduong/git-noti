import hashlib
import hmac


class GitHubWebhook:
    def __init__(self, secret: str, body: bytes, signature: str | None) -> None:
        self._secret = secret
        self._body = body
        self._signature = signature

    def verify_signature(self) -> None:
        if not self._secret or not self._signature:
            raise ValueError("Missing webhook secret or signature")

        expected = f"sha256={hmac.new(self._secret.encode('utf-8'), self._body, hashlib.sha256).hexdigest()}"
        if not hmac.compare_digest(self._signature, expected):
            raise ValueError("Invalid webhook signature")
