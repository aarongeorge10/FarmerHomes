from django.urls import path
from .views import farmer_weather,public_weather

urlpatterns = [
    path("farmer/", farmer_weather, name="farmer_weather"),
    path("advisory/", public_weather, name="public_weather"),
]