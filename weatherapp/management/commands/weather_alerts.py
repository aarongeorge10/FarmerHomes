from django.core.management.base import BaseCommand
from weatherapp.alerts import run_weather_alerts


class Command(BaseCommand):
    help = "Send weather based crop alerts to farmers"

    def handle(self, *args, **kwargs):
        run_weather_alerts()
        self.stdout.write("Weather alerts sent successfully")
