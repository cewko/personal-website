import requests
from decouple import config
from datetime import datetime, timezone
from .base import BaseIntegrationService


class LastFmService(BaseIntegrationService):
    cache_timeout = 60
    task_name = "apps.integrations.tasks.refresh_lastfm_track"

    def __init__(self):
        self.api_key = config("LASTFM_API_KEY", default="")
        self.username = config("LASTFM_USERNAME", default="")
        self.api_url = "http://ws.audioscrobbler.com/2.0/"

    def get_cache_key(self):
        return f"integration:lastfm:{self.username}"

    def fetch_data(self):
        if not self.api_key or not self.username:
            return None

        try:
            params = {
                "method": "user.getrecenttracks",
                "user": self.username,
                "api_key": self.api_key,
                "format": "json",
                "limit": 1,
                "extended": 1,
            }

            response = requests.get(self.api_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            tracks = data.get("recenttracks", {}).get("track", [])
            if not tracks:
                return None

            track = next(
                (t for t in tracks if t.get("@attr", {}).get("nowplaying") == "true"),
                tracks[0],
            )

            artist = track.get("artist", {})
            if isinstance(artist, dict):
                artist_name = artist.get("name") or artist.get("#text") or "unknown"
            else:
                artist_name = str(artist) if artist else "unknown"

            track_name = track.get("name") or "Unknown Song"

            images = track.get("image", [])
            cover_url = next(
                (img.get("#text") for img in reversed(images) if img.get("#text")), None
            )

            timestamp = None
            time_ago = None
            if track.get("@attr", {}).get("nowplaying") == "true":
                time_ago = "playing now"
            else:
                date_info = track.get("date", {})
                if "uts" in date_info:
                    timestamp = int(date_info["uts"])
                    time_ago = self._format_time_ago(timestamp)

            track_url = track.get("url") or "#"

            return {
                "artist": artist_name,
                "name": track_name,
                "cover_url": cover_url,
                "timestamp": timestamp,
                "time_ago": time_ago,
                "url": track_url,
            }

        except requests.RequestException:
            return None
        except (KeyError, ValueError, TypeError):
            return None


    @staticmethod
    def _format_time_ago(unix_timestamp):
        now = datetime.now(timezone.utc)
        track_time = datetime.fromtimestamp(unix_timestamp, timezone.utc)
        
        diff = now - track_time
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "playing now"
        
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