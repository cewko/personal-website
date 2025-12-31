import requests
from decouple import config
from .base import BaseIntegrationService


class DiscordService(BaseIntegrationService):
    cache_timeout = 300
    task_name = "apps.integrations.tasks.refresh_discord_status"

    def __init__(self):
        self.user_id = config("DISCORD_USER_ID", default="")
        self.api_url = f"https://api.lanyard.rest/v1/users/{self.user_id}"

    def get_cache_key(self):
        return f"integration:discord:{self.user_id}"

    def fetch_data(self):
        if not self.user_id:
            return None

        try:
            response = requests.get(self.api_url, timeout=5)
            response.raise_for_status()

            data = response.json()

            if data.get("success") and "data" in data:
                discord_data = data["data"]
                status = discord_data.get("discord_status", "offline")

                return {
                    "status": self._normalize_status(status),
                    "raw_status": status,
                }

            return None

        except requests.RequestException:
            return None

    def _normalize_status(self, status):
        if status in ("online", "idle", "dnb"):
            status = "online"

        return status