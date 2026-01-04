from django.shortcuts import render, redirect, get_object_or_404
from farmersaccapp.models import AllUser, BuyerProfile
from buyersapp.models import BuyerBuyPrice, BuyerSellProduct
from farmersaccapp.decorators import buyer_required
from products.models import Product
from markets.models import Market
from farmersaccapp.models import FarmerProfile
from trading.models import MarketCartItem
from trading.models import MarketSellOrder


@buyer_required
def buyer_dashboard(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    user = get_object_or_404(AllUser, id=user_id, role="buyer")
    buyer = get_object_or_404(BuyerProfile, user=user)

    # 🔹 RECENT BUY PRICES
    buy_prices = (
        BuyerBuyPrice.objects
        .filter(buyer=buyer)
        .select_related("product", "market")
        .order_by("-updated_at")[:3]
    )

    # 🔹 RECENT SHOP PRODUCTS
    shop_products = (
        BuyerSellProduct.objects
        .filter(buyer=buyer)
        .select_related("product", "market")
        .order_by("-created_at")[:3]
    )

    # 🔴 PENDING FARMER ORDERS (ACTION REQUIRED)
    pending_orders = (
        MarketSellOrder.objects
        .filter(buyer=buyer, status="pending")
        .select_related("farmer", "market")
        .prefetch_related("items")
        .order_by("-created_at")
    )

    # 🟢 LAST 3 APPROVED ORDERS (HISTORY PREVIEW)
    approved_orders = (
        MarketSellOrder.objects
        .filter(buyer=buyer, status="approved")
        .select_related("farmer", "market")
        .order_by("-created_at")[:3]
    )

    return render(request, "buyer/buyer_dashboard.html", {
        "buyer": buyer,
        "buy_prices": buy_prices,
        "shop_products": shop_products,
        "pending_orders": pending_orders,
        "approved_orders": approved_orders,
    })


@buyer_required
def buyer_buying_prices(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = get_object_or_404(AllUser, id=user_id, role="buyer")
    buyer = get_object_or_404(BuyerProfile, user=user)

    buy_prices = BuyerBuyPrice.objects.filter(buyer=buyer)
    markets = Market.objects.filter(is_active=True)

    return render(request, "buyer/buying_prices.html", {
        "buyer": buyer,
        "buy_prices": buy_prices,
        "markets": markets
    })


@buyer_required
def add_buying_price(request):
    user_id = request.session.get("user_id")
    user = get_object_or_404(AllUser, id=user_id, role="buyer")
    buyer = get_object_or_404(BuyerProfile, user=user)

    if request.method == "POST":
        BuyerBuyPrice.objects.create(
            buyer=buyer,
            market_id=request.POST["market"],   # ✅ NEW
            product_id=request.POST["product"],
            price_per_unit=request.POST["price"],
            unit=request.POST["unit"],
            min_quantity=request.POST["min_quantity"],
        )
        return redirect("buyer_buying_prices")

    products = Product.objects.filter(is_active=True)
    markets = Market.objects.filter(is_active=True)

    return render(request, "buyer/add_buying_price.html", {
        "products": products,
        "markets": markets
    })

@buyer_required
def edit_buying_price(request, price_id):
    user_id = request.session.get("user_id")
    user = get_object_or_404(AllUser, id=user_id, role="buyer")
    buyer = get_object_or_404(BuyerProfile, user=user)

    price = get_object_or_404(BuyerBuyPrice, id=price_id, buyer=buyer)

    if request.method == "POST":
        price.market_id = request.POST["market"]   # ✅ THIS WAS MISSING
        price.price_per_unit = request.POST["price_per_unit"]
        price.min_quantity = request.POST["min_quantity"]
        price.unit = request.POST["unit"]
        price.save()

        return redirect("buyer_buying_prices")

    markets = Market.objects.filter(is_active=True)

    return render(request, "buyer/edit_buying_price.html", {
        "price": price,
        "markets": markets
    })
@buyer_required
def toggle_buying_price(request, price_id):
    user_id = request.session.get("user_id")
    user = get_object_or_404(AllUser, id=user_id, role="buyer")
    buyer = get_object_or_404(BuyerProfile, user=user)

    price = get_object_or_404(BuyerBuyPrice, id=price_id, buyer=buyer)

    price.is_active = not price.is_active
    price.save()

    return redirect("buyer_buying_prices")




@buyer_required
def buyer_shop_products(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = get_object_or_404(AllUser, id=user_id, role="buyer")
    buyer = get_object_or_404(BuyerProfile, user=user)

    shop_products = BuyerSellProduct.objects.filter(
        buyer=buyer
    ).select_related("product", "market")

    return render(request, "buyer/shop_products.html", {
        "buyer": buyer,
        "shop_products": shop_products
    })


@buyer_required
def add_shop_product(request):
    user_id = request.session.get("user_id")
    user = get_object_or_404(AllUser, id=user_id, role="buyer")
    buyer = get_object_or_404(BuyerProfile, user=user)

    products = Product.objects.filter(is_active=True)
    markets = Market.objects.filter(is_active=True)

    if request.method == "POST":
        BuyerSellProduct.objects.create(
            buyer=buyer,
            market_id=int(request.POST["market"]),
            product_id=int(request.POST["product"]),
            price=float(request.POST["price"]),
            stock_quantity=int(request.POST["stock_quantity"]),  # ✅ FIX
            unit=request.POST["unit"]
        )
        return redirect("buyer_shop_products")

    return render(request, "buyer/add_shop_product.html", {
        "products": products,
        "markets": markets
    })



@buyer_required
def edit_shop_product(request, product_id):
    user_id = request.session.get("user_id")
    user = get_object_or_404(AllUser, id=user_id, role="buyer")
    buyer = get_object_or_404(BuyerProfile, user=user)

    shop_product = get_object_or_404(
        BuyerSellProduct,
        id=product_id,
        buyer=buyer
    )

    markets = Market.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)

    if request.method == "POST":
        shop_product.market_id = int(request.POST["market"])
        shop_product.product_id = int(request.POST["product"])
        shop_product.price = float(request.POST["price"])
        shop_product.stock_quantity = int(request.POST["stock_quantity"])  # ✅ FIX
        shop_product.unit = request.POST["unit"]
        shop_product.save()

        return redirect("buyer_shop_products")

    return render(request, "buyer/edit_shop_product.html", {
        "shop_product": shop_product,
        "markets": markets,
        "products": products
    })

@buyer_required
def toggle_shop_product(request, product_id):
    user_id = request.session.get("user_id")
    user = get_object_or_404(AllUser, id=user_id, role="buyer")
    buyer = get_object_or_404(BuyerProfile, user=user)

    shop_product = get_object_or_404(
        BuyerSellProduct,
        id=product_id,
        buyer=buyer
    )

    # 🚫 Do not allow activation if stock is zero
    if shop_product.stock_quantity <= 0:
        shop_product.is_available = False
    else:
        shop_product.is_available = not shop_product.is_available

    shop_product.save()
    return redirect("buyer_shop_products")



def market_buying_prices(request, market_id):
    market = get_object_or_404(Market, id=market_id, is_active=True)

    buying_prices = (
        BuyerBuyPrice.objects
        .filter(market=market, is_active=True)
        .select_related("product", "buyer")
    )

    farmer = get_object_or_404(
        FarmerProfile,
        user_id=request.session.get("user_id")
    )

    # ✅ CART COUNT (NO CONTEXT PROCESSOR)
    cart_count = MarketCartItem.objects.filter(
        cart__farmer=farmer
    ).count()

    return render(request, "markets/market_buying_prices.html", {
        "market": market,
        "buying_prices": buying_prices,
        "cart_count": cart_count
    })


