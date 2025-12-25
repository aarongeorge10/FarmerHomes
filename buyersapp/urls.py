# buyers/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("buyer_dashboard/", views.buyer_dashboard, name="buyer_dashboard"),
    path("add-buying-price/", views.add_buying_price, name="add_buying_price"),
    path("buying-price/edit/<int:price_id>/", views.edit_buying_price, name="edit_buying_price"),
    path("buying-price/toggle/<int:price_id>/", views.toggle_buying_price, name="toggle_buying_price"),
]
