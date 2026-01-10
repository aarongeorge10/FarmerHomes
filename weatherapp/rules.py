def get_crop_advice(crop, weather):
    temp = weather["temperature"]
    rain = weather["rain"]
    humidity = weather["humidity"]
    wind = weather["wind_speed"]

    # 🌾 CEREALS
    if crop in ["rice"]:
        if rain < 2 and temp > 32:
            return "☀️ Hot & dry. Increase irrigation for rice."
        if rain > 15:
            return "🌧️ Heavy rain expected. Drain excess water from rice fields."
        if humidity > 85:
            return "🦠 High humidity → risk of rice blast disease."

    if crop in ["wheat"]:
        if temp > 30:
            return "🔥 High temperature may reduce wheat yield. Irrigate lightly."
        if humidity > 80:
            return "⚠️ High humidity → risk of wheat rust disease."
        if rain > 10:
            return "🌧️ Avoid fertilizer application in wheat today."

    if crop in ["maize"]:
        if rain < 3:
            return "🌞 Low rainfall. Irrigate maize fields."
        if temp > 34:
            return "🔥 Heat stress risk in maize. Increase watering."
        if humidity > 80:
            return "🦠 Risk of leaf blight in maize."

    if crop in ["millet", "sorghum", "ragi"]:
        if rain > 5:
            return "🌧️ Rain detected. Do NOT irrigate millet/jowar/ragi fields."
        if temp > 35:
            return "☀️ High temperature. Light irrigation recommended."
        if humidity > 80:
            return "⚠️ High humidity → fungal risk in millets."

    # 🌱 PULSES
    if crop in ["gram", "pigeon_pea", "lentil", "mung", "urad", "pea"]:
        if rain > 10:
            return "🌧️ Excess rain → waterlogging risk for pulses. Improve drainage."
        if temp > 35:
            return "☀️ Heat stress. Light irrigation recommended for pulses."
        if humidity > 85:
            return "🦠 High humidity → risk of wilt & fungal disease in pulses."

    # 🌻 OILSEEDS
    if crop in ["mustard", "sunflower", "soybean", "groundnut", "sesame", "castor"]:
        if rain < 3:
            return "🌞 Low rainfall. Irrigate oilseed crops."
        if humidity > 80:
            return "🐛 High humidity → pest & fungal attack risk in oilseeds."
        if rain > 15:
            return "🌧️ Heavy rain → avoid fertilizer spraying today."

    # 🌿 FIBER CROPS
    if crop in ["cotton", "jute"]:
        if rain < 2 and temp > 35:
            return "☀️ Hot & dry. Water cotton/jute crops immediately."
        if humidity > 80:
            return "🐛 High humidity → bollworm & fungal attack risk."
        if wind > 6:
            return "🌬️ Strong wind. Avoid pesticide spraying today."

    # 🌴 CASH CROPS
    if crop in ["sugarcane"]:
        if rain < 3:
            return "🌞 Low rainfall. Increase irrigation for sugarcane."
        if rain > 20:
            return "🌧️ Excess rain → ensure proper drainage for sugarcane."
        if humidity > 85:
            return "🦠 High humidity → risk of red rot disease."

    # 🥬 VEGETABLES
    if crop in ["tomato", "chilli", "brinjal", "cabbage", "cauliflower", "okra", "onion", "potato"]:
        if rain > 10:
            return "🌧️ Heavy rain → avoid irrigation & pesticide spraying for vegetables."
        if temp > 35:
            return "☀️ Heat stress → increase watering for vegetables."
        if humidity > 80:
            return "🦠 High humidity → fungal disease risk in vegetables."

    # 🍎 FRUITS
    if crop in ["banana", "mango", "grapes", "orange", "pomegranate", "apple", "papaya"]:
        if rain > 15:
            return "🌧️ Heavy rain → ensure drainage to prevent root rot in fruit crops."
        if temp > 35:
            return "☀️ High heat → irrigate fruit orchards adequately."
        if humidity > 85:
            return "🦠 High humidity → risk of fruit fungal disease."

    return None
