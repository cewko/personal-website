import re
import html
import requests
from datetime import datetime, timezone
from decouple import config
from django.utils.html import strip_tags
from .base import BaseIntegrationService


class MastodonService(BaseIntegrationService):
    cache_timeout = 1800

    def __init__(self):
        self.instance = config("MASTODON_INSTANCE", default="")
        self.username = config("MASTODON_USERNAME", default="")
        self.api_url = f"https://{self.instance}/api/v1"

    def get_cache_key(self):
        return f"integration:mastodon:{self.username}"

    def fetch_data(self):
        if not self.instance or not self.username:
            return None

        try:
            account_url = f"{self.api_url}/accounts/lookup"
            account_params = {"acct": self.username}
        
            account_response = requests.get(
                account_url,
                params=account_params,
                timeout=5
            )
            account_response.raise_for_status()
            account_data = account_response.json()
            account_id = account_data['id']

            statuses_url = f"{self.api_url}/accounts/{account_id}/statuses"
            statuses_params = {
                "limit": 1,
                "exclude_replies": "true",
                "exclude_reblogs": "false"
            }

            statuses_response = requests.get(
                statuses_url,
                params=statuses_params,
                timeout=5
            )
            statuses_response.raise_for_status()
            statuses = statuses_response.json()
            
            if not statuses:
                return None

            status = statuses[0]

            created_at = datetime.fromisoformat(
                status["created_at"].replace("Z", "+00:00")
            )

            content = status['content']
            content = re.sub(r'<a[^>]*href="[^"]*"[^>]*>.*?</a>', '[link] ', content, flags=re.DOTALL)
            content = strip_tags(content)
            content = html.unescape(content)
            
            media_text = ""
            if status.get("media_attachments"):
                media_counts = {}
                for media in status["media_attachments"]:
                    media_type = media["type"]
                    media_counts[media_type] = media_counts.get(media_type, 0) + 1

                media_parts = []
                for media_type, count in media_counts.items():
                    if count == 1:
                        if media_type == 'image':
                            media_parts.append('[image]')
                        elif media_type == 'video':
                            media_parts.append('[video]')
                        elif media_type == 'gifv':
                            media_parts.append('[gif]')
                        elif media_type == 'audio':
                            media_parts.append('[audio]')
                    else:
                        if media_type == 'image':
                            media_parts.append(f'[{count} images]')
                        elif media_type == 'video':
                            media_parts.append(f'[{count} videos]')
                        elif media_type == 'gifv':
                            media_parts.append(f'[{count} gifs]')
                        elif media_type == 'audio':
                            media_parts.append(f'[{count} audios]')
                
                if media_parts:
                    content = content + ' ' + ' '.join(media_parts)

            return {
                'content': content,
                'url': status.get("url", f"https://{self.username}/@{self.username}"),
                'created_at': self._format_time_ago(created_at),
                'username': account_data['username'],
                'avatar': account_data['avatar'],
            }

        except requests.Timeout:
            return None
        except requests.RequestException as e:
            return None
        except (KeyError, ValueError, TypeError) as e:
            return None

    @staticmethod
    def _format_time_ago(created_at):
        now = datetime.now(timezone.utc)
        diff = now - created_at
        seconds = diff.total_seconds()

        if seconds < 60:
            return "moment ago"
        minutes = int(seconds / 60)
        if minutes < 60:
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        hours = int(minutes / 60)
        if hours < 24:
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        days = int(hours / 24)
        if days < 30:
            return f"{days} day{'s' if days != 1 else ''} ago"
        months = int(days / 30)
        if months < 12:
            return f"{months} month{'s' if months != 1 else ''} ago"
        years = int(months / 12)
        return f"{years} year{'s' if years != 1 else ''} ago"
