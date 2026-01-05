from django.shortcuts import render, redirect, get_object_or_404
from .models import Market
from .utils import haversine
from farmersaccapp.decorators import admin_required, farmer_required
from farmersaccapp.models import AllUser
from farmersaccapp.models import FarmerProfile
from buyersapp.models import BuyerBuyPrice
from buyersapp.models import BuyerSellProduct



# =========================
# ADMIN VIEWS
# =========================

@admin_required
def admin_markets(request):
    markets = Market.objects.all()
    return render(request, "admin/markets_list.html", {
        "markets": markets
    })


@admin_required
def add_market(request):
    if request.method == "POST":
        Market.objects.create(
            name=request.POST.get("name"),
            address=request.POST.get("address"),
            village=request.POST.get("village"),
            district=request.POST.get("district"),
            state=request.POST.get("state"),
            latitude=float(request.POST.get("latitude")) if request.POST.get("latitude") else None,
            longitude=float(request.POST.get("longitude")) if request.POST.get("longitude") else None,
        )
        return redirect("admin_markets")

    return render(request, "admin/add_market.html")


# =========================
# USER / FARMER VIEWS
# =========================

def user_markets(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    user = AllUser.objects.get(id=user_id)
    farmer = user.farmer_profile

    markets = Market.objects.filter(
        district__iexact=farmer.district,
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

def public_market_products(request, market_id):
    market = get_object_or_404(Market, id=market_id, is_active=True)

    products = BuyerSellProduct.objects.filter(
        market=market,
        is_available=True
    ).select_related(
        "product",
        "buyer"
    )

    return render(request, "markets/public_market_products.html", {
        "market": market,
        "products": products
    })


def nearest_markets(request):
    farmer = get_object_or_404(
        FarmerProfile,
        user_id=request.session.get("user_id")
    )

    has_location = farmer.latitude and farmer.longitude
    markets_data = []

    if has_location:
        markets = Market.objects.filter(is_active=True)

        for market in markets:
            distance = haversine(
                farmer.latitude,
                farmer.longitude,
                float(market.latitude),
                float(market.longitude)
            )
            markets_data.append({
                "market": market,
                "distance": distance
            })

        markets_data.sort(key=lambda x: x["distance"])

    return render(request, "markets/nearest_markets.html", {
        "markets": markets_data,
        "has_location": has_location
    })


def market_products(request, market_id):
    market = get_object_or_404(Market, id=market_id)

    category = request.GET.get("category")

    products = BuyerSellProduct.objects.filter(
        market=market
    ).select_related(
        "product",
        "buyer",
        "buyer__user"
    )

    # 🔍 Optional category filter
    if category:
        products = products.filter(
            product__category__key=category
        )

    # 🔍 Only available products
    products = products.filter(is_available=True)

    return render(request, "markets/market_products.html", {
        "market": market,
        "products": products
    })


@farmer_required
def seed_markets(request):
    user = request.current_user
    farmer = user.farmer_profile

    markets = Market.objects.filter(
        is_active=True,
        latitude__isnull=False,
        longitude__isnull=False
    )

    market_list = []

    if farmer.latitude and farmer.longitude:
        for market in markets:
            has_seeds = BuyerSellProduct.objects.filter(
                market=market,
                product__category__key="seed",
                is_available=True
            ).exists()

            if has_seeds:
                distance = haversine(
                    float(farmer.latitude),
                    float(farmer.longitude),
                    float(market.latitude),
                    float(market.longitude)
                )

                market_list.append({
                    "market": market,
                    "distance": round(distance, 2)
                })

        market_list.sort(key=lambda x: x["distance"])

    return render(request, "markets/seed_markets.html", {
        "markets": market_list
    })
