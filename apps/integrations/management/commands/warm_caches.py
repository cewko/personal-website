from django.core.management.base import BaseCommand
from apps.integrations.services import (
    DiscordService,
    LastFmService,
    WeatherService,
    WakatimeService,
    BlueskyService,
    GithubService
)


class Command(BaseCommand):
    help = 'Warm all integration caches (run after deployment).'

    def handle(self, *args, **options):
        self.stdout.write("Warming integration caches...")
        
        services = [
            (DiscordService, "Discord"),
            (LastFmService, "Last.fm"),
            (WeatherService, "Weather"),
            (WakatimeService, "WakaTime"),
            (BlueskyService, "Bluesky"),
            (GithubService, "GitHub"),
        ]
        
        success_count = 0
        
        for service_class, name in services:
            try:
                self.stdout.write(f"Fetching {name}...", ending="")
                service = service_class()
                data = service.fetch_and_cache()
                
                if data:
                    self.stdout.write(self.style.SUCCESS(" OK"))
                    success_count += 1
                else:
                    self.stdout.write(self.style.WARNING(" No data"))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f" Error: {e}"))
        
        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(f"Cache warming complete: {success_count}/{len(services)} services")
        )