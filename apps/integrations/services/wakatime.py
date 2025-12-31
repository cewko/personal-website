import requests
from decouple import config
from .base import BaseIntegrationService


class WakatimeService(BaseIntegrationService):
    cache_timeout = 3600
    task_name = "apps.integrations.tasks.refresh_wakatime_stats"
    
    def __init__(self):
        self.api_key = config('WAKATIME_API_KEY', default='')
        self.api_url = "https://wakatime.com/api/v1/users/current/all_time_since_today"
    
    def get_cache_key(self):
        return f"integration:wakatime:stats"
    
    def fetch_data(self):
        if not self.api_key:
            return None
        
        try:
            params = {
                "api_key": self.api_key
            }
            
            response = requests.get(self.api_url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' not in data:
                return None
            
            stats = data['data']

            total_hours, total_minutes = self._seconds_to_hours_minutes(
                stats.get("total_seconds", 0)
            )
            daily_hours, daily_minutes = self._seconds_to_hours_minutes(
                stats.get("daily_average", 0)
            )
            
            return {
                'total_hours': total_hours,
                'total_minutes': total_minutes,
                'daily_hours': daily_hours,
                'daily_minutes': daily_minutes,
            }
            
        except requests.RequestException:
            return None
        except Exception:
            return None

    @staticmethod
    def _seconds_to_hours_minutes(seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return int(hours), int(minutes)