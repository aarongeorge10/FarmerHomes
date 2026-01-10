from farmersaccapp.models import FarmerProfile
from trading.models import FarmerNotification
from weatherapp.services import get_weather
from weatherapp.rules import get_crop_advice


def run_weather_alerts():
    farmers = FarmerProfile.objects.exclude(latitude=None).exclude(crop=None)

    for farmer in farmers:
        try:
            weather = get_weather(farmer.latitude, farmer.longitude)
            advice = get_crop_advice(farmer.crop, weather)

            if advice and not FarmerNotification.objects.filter(
                farmer=farmer,
                message=advice
            ).exists():
                FarmerNotification.objects.create(
                    farmer=farmer,
                    message=advice
                )

        except Exception as e:
            print("Weather error for", farmer.user.username, e)
