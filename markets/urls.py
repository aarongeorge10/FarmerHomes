from django.urls import path
from . import views

urlpatterns = [

    # =========================
    # ADMIN (CUSTOM ADMIN PANEL)
    # =========================
    path("admin/", views.admin_markets, name="admin_markets"),
    path("admin/add/", views.add_market, name="add_market"),

    # =========================
    # USER / FARMER
    # =========================
    path("nearby/", views.user_markets, name="user_markets"),
    path("nearest/", views.nearest_markets, name="nearest_markets"),
    path("seed-markets/", views.seed_markets, name="seed_markets"),

    # =========================
    # PUBLIC
    # =========================
    path("all/", views.public_markets, name="public_markets"),
    path("market/<int:market_id>/products/", views.market_products, name="market_products"),
]
