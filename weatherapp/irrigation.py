def irrigation_schedule(crop, forecast):
    schedule = []

    for day in forecast[:5]:   # next 5 days
        temp = day["temp"]["day"]
        rain = day.get("rain", 0)

        if rain > 5:
            schedule.append("🌧 No irrigation (Rain expected)")
        elif temp > 35:
            schedule.append("☀ Increase irrigation")
        elif temp < 25:
            schedule.append("💧 Light irrigation")
        else:
            schedule.append("✅ Normal irrigation")

    return schedule
