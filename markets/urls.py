from django.urls import path
from . import views
from buyersapp.views import market_buying_prices
urlpatterns = [

    # =========================
    # ADMIN
    # =========================
    path("admin/", views.admin_markets, name="admin_markets"),
    path("admin/add/", views.add_market, name="add_market"),

    # =========================
    # FARMER
    # =========================
    path("nearby/", views.user_markets, name="user_markets"),
    path("nearest/", views.nearest_markets, name="nearest_markets"),
    path("farmer/markets/", views.farmer_markets, name="farmer_markets"),
path("markets/<int:market_id>/products/", views.market_products, name="market_products"),

    # 👉 IMPORTED FROM buyersapp.views
    path("market/<int:market_id>/buyers/", market_buying_prices, name="market_buying_prices"),
    # =========================
    # PUBLIC
    # =========================
    path("all/", views.public_markets, name="public_markets"),
    path("public/<int:market_id>/products/", views.public_market_products, name="public_market_products"),
]
