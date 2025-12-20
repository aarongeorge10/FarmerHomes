from django.urls import path
from . import views 

urlpatterns = [
    # Admin
    path("admin/", views.admin_markets, name="admin_markets"),
    path("admin/add/", views.add_market, name="add_market"),

    # User
    path("nearby/", views.user_markets, name="user_markets"),
    path("all/", views.public_markets, name="public_markets"),
    path("nearest/", views.nearest_markets, name="nearest_markets"),
    path("market/<int:market_id>/products/", views.market_products, name="market_products"),
]
