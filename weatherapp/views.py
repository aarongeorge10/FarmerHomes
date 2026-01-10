from django.shortcuts import render, redirect
from farmersaccapp.decorators import farmer_required
from weatherapp.services import get_weather
from weatherapp.rules import get_crop_advice
from weatherapp.irrigation import irrigation_schedule

@farmer_required
def farmer_weather(request):
    farmer = request.current_user.farmer_profile

    # If farmer has not set location
    if not farmer.latitude or not farmer.longitude:
        return redirect("farmer_profile")

    weather = get_weather(farmer.latitude, farmer.longitude)

    advice = get_crop_advice(farmer.crop, weather)
    schedule = irrigation_schedule(farmer.crop, weather["forecast"])
    
    return render(request, "weather/farmer_weather.html", {
    "weather": weather,
    "advice": advice,
    "crop": farmer.crop,
    "schedule": schedule
})


def public_weather(request):
    # Use a fixed central India location (or admin-selected later)
    lat = 20.5937   # India center
    lon = 78.9629

    weather = get_weather(lat, lon)

    rules = [
        "🌧️ If rain > 5mm → Avoid irrigation",
        "☀️ If temperature > 35°C → Increase watering",
        "💧 If humidity > 80% → Risk of fungal disease",
        "🌬️ If wind > 6 m/s → Avoid pesticide spraying",
        "🌱 Best time to irrigate: Early morning or evening"
    ]

    return render(request, "weather/public_weather.html", {
        "weather": weather,
        "rules": rules
    })

