from django.shortcuts import render, redirect, get_object_or_404
from .models import Market
from farmersaccapp.decorators import admin_required,farmer_required
from .utils import haversine
from farmersaccapp.models import AllUser
from products.models import MarketProduct

@admin_required
def admin_markets(request):
    markets = Market.objects.all()
    return render(request, "admin/markets_list.html", {"markets": markets})


@admin_required
def add_market(request):
    if request.method == "POST":
        Market.objects.create(
            name=request.POST["name"],
            address=request.POST["address"],
            village=request.POST["village"],
            district=request.POST["district"],
            state=request.POST["state"],
            latitude=request.POST["latitude"],
            longitude=request.POST["longitude"],
        )
        return redirect("admin_markets")

    return render(request, "admin/add_market.html")


def user_markets(request):
    user = request.user

    # Example: using farmer profile location
    district = user.farmer_profile.district

    markets = Market.objects.filter(
        district__iexact=district,
        is_active=True
    )

    return render(request, "user/markets.html", {
        "markets": markets
    })

def public_markets(request):
    markets = Market.objects.filter(is_active=True)
    return render(request, "markets/public_markets.html", {
        "markets": markets
    })

@farmer_required
def nearest_markets(request):
    user_id = request.session.get("user_id")
    user = AllUser.objects.get(id=user_id)
    farmer = user.farmer_profile

    markets = Market.objects.filter(
        is_active=True,
        latitude__isnull=False,
        longitude__isnull=False
    )

    market_list = []

    if farmer.latitude and farmer.longitude:
        for market in markets:
            distance = haversine(
                float(farmer.latitude),
                float(farmer.longitude),
                float(market.latitude),
                float(market.longitude)
            )
            market_list.append({
                "market": market,
                "distance": distance
            })

        market_list.sort(key=lambda x: x["distance"])
    else:
        for market in markets:
            market_list.append({
                "market": market,
                "distance": None
            })

    return render(request, "markets/nearest_markets.html", {
        "markets": market_list
    })


def market_products(request, market_id):
    market = get_object_or_404(Market, id=market_id)
    products = MarketProduct.objects.filter(
        market=market,
        is_active=True
    )

    return render(request, "markets/market_products.html", {
        "market": market,
        "products": products
    })