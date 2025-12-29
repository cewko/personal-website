from django import template
from apps.integrations.services import (
    DiscordService, 
    LastFmService, 
    WeatherService,
    WakatimeService,
    BlueskyService,
    GithubService
)

register = template.Library()


@register.inclusion_tag("integrations/discord_status.html")
def discord_status_widget():
    service = DiscordService()
    data = service.get_data()

    status = "down"
    if data:
        status = data["status"]

    return {"status": status}


@register.inclusion_tag('integrations/lastfm_widget.html')
def lastfm_widget():
    service = LastFmService()
    data = service.get_data()
    
    return {'track': data}


@register.inclusion_tag('integrations/weather_widget.html')
def weather_widget():
    service = WeatherService()
    weather_data = service.get_data()

    if not weather_data:
        weather_data = {
            "temperature": "--",
            "humidity": "--",
            "description": "The West has fallen"
        }

    return {'weather': weather_data}


@register.inclusion_tag('integrations/wakatime_widget.html')
def wakatime_widget():
    service = WakatimeService()
    wakatime_data = service.get_data()

    if not wakatime_data:
        wakatime_data = {
            "total_hours": "00",
            "total_minutes": "00",
            "daily_hours": "00",
            "daily_minutes": "00"
        }

    return {'stats': wakatime_data}


@register.inclusion_tag("integrations/bluesky_widget.html")
def bluesky_widget():
    service = BlueskyService()
    data = service.get_data()

    return {"status": data}


@register.inclusion_tag("integrations/github_widget.html")
def github_widget():
    service = GithubService()
    data = service.get_data()

    return {"github": data}