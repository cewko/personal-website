import re
import html
import requests
from datetime import datetime, timezone
from decouple import config
from django.utils.html import strip_tags
from .base import BaseIntegrationService


class BlueskyService(BaseIntegrationService):
    cache_timeout = 1800

    def __init__(self):
        self.handle = config("BLUESKY_HANDLE", default="")
        self.api_url = "https://public.api.bsky.app/xrpc"

    def get_cache_key(self):
        return f"integration:bluesky:{self.handle}"

    def fetch_data(self):
        if not self.handle:
            return None

        try:
            resolve_url = f"{self.api_url}/com.atproto.identity.resolveHandle"
            resolve_params = {"handle": self.handle}
            
            resolve_response = requests.get(
                resolve_url,
                params=resolve_params,
                timeout=5
            )
            resolve_response.raise_for_status()
            did = resolve_response.json()['did']

            profile_url = f"{self.api_url}/app.bsky.actor.getProfile"
            profile_params = {"actor": did}
            
            profile_response = requests.get(
                profile_url,
                params=profile_params,
                timeout=5
            )
            profile_response.raise_for_status()
            profile_data = profile_response.json()

            feed_url = f"{self.api_url}/app.bsky.feed.getAuthorFeed"
            feed_params = {
                "actor": did,
                "limit": 1,
                "filter": "posts_no_replies"
            }

            feed_response = requests.get(
                feed_url,
                params=feed_params,
                timeout=5
            )
            feed_response.raise_for_status()
            feed_data = feed_response.json()
            
            if not feed_data.get("feed"):
                return None

            post = feed_data["feed"][0]["post"]

            created_at = datetime.fromisoformat(
                post["record"]["createdAt"].replace("Z", "+00:00")
            )
            content = post["record"].get("text", "")
            
            if post["record"].get("facets"):
                pass
            
            if post.get("embed"):
                embed = post["embed"]
                
                if embed.get("$type") == "app.bsky.embed.images#view":
                    image_count = len(embed.get("images", []))
                    if image_count == 1:
                        content += " [ image ]"
                    else:
                        content += f" [ {image_count} images ]"
                        
                elif embed.get("$type") == "app.bsky.embed.video#view":
                    content += " [ video ]"
                    
                elif embed.get("$type") == "app.bsky.embed.external#view":
                    content += " [ link ]"
                    
                elif embed.get("$type") == "app.bsky.embed.record#view":
                    content += " [ quote ]"
                    
                elif embed.get("$type") == "app.bsky.embed.recordWithMedia#view":
                    if embed.get("media", {}).get("$type") == "app.bsky.embed.images#view":
                        image_count = len(embed["media"].get("images", []))
                        content += f" [ {image_count} image{'s' if image_count > 1 else ''} + quote ]"

            post_uri = post["uri"]
            uri_parts = post_uri.replace("at://", "").split("/")
            rkey = uri_parts[-1]
            post_url = f"https://bsky.app/profile/{self.handle}/post/{rkey}"

            return {
                'content': content.strip(),
                'url': post_url,
                'created_at': self._format_time_ago(created_at),
                'username': profile_data.get("displayName") or profile_data.get("handle"),
                'avatar': profile_data.get("avatar", ""),
                'handle': profile_data.get("handle"),
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