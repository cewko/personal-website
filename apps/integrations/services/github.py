import requests
from decouple import config
from datetime import datetime, timedelta
from .base import BaseIntegrationService


class GithubService(BaseIntegrationService):
    cache_timeout = 7200
    task_name = "apps.integrations.tasks.refresh_github_contributions"

    def __init__(self):
        self.username = config("GITHUB_USERNAME", default="")
        self.access_token = config("GITHUB_ACCESS_TOKEN", default="")
        self.api_url = "https://api.github.com/graphql"

    def get_cache_key(self):
        return f"integration:github:{self.username}"
    
    def fetch_data(self):
        if not self.username or not self.access_token:
            return None

        query = """
        query($username: String!) {
          user(login: $username) {
            contributionsCollection {
              contributionCalendar {
                totalContributions
                weeks {
                  contributionDays {
                    contributionCount
                    date
                    color
                  }
                }
              }
            }
          }
        }
        """

        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
            }
            
            payload = {
                'query': query,
                'variables': {'username': self.username}
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()

            if "data" not in data or "user" not in data["data"]:
                return None

            calendar = data['data']['user']['contributionsCollection']['contributionCalendar']

            weeks = []
            for week in calendar["weeks"]:
                week_days = []
                for day in week["contributionDays"]:
                    week_days.append(
                        {
                            "date": day["date"],
                            "count": day["contributionCount"],
                            "color": day["color"]
                        }
                    )
                weeks.append(week_days)

            days = []
            for week in weeks:
                days.extend(week)

            current_streak = self._calculate_current_streak(days)
            longest_streak = self._calculate_longest_streak(days)

            return {
                "total_contributions": calendar["totalContributions"],
                "weeks": weeks,
                "current_streak": current_streak,
                "longest_streak": longest_streak
            }

        except requests.Timeout:
            return None
        except requests.RequestException as e:
            return None
        except (KeyError, ValueError, TypeError) as e:
            return None

    @staticmethod
    def _calculate_current_streak(days):
        if not days:
            return 0
        
        streak = 0
        for day in reversed(days):
            if day["count"] > 0:
                streak += 1
            else:
                break

        return streak

    @staticmethod
    def _calculate_longest_streak(days):
        if not days:
            return 0

        longest = 0
        current = 0

        for day in days:
            if day["count"] > 0:
                current += 1
                longest = max(current, longest)
            else:
                current = 0

        return longest