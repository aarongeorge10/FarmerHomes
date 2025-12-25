from django.shortcuts import render, redirect, get_object_or_404
from farmersaccapp.models import AllUser, BuyerProfile
from buyersapp.models import BuyerBuyPrice, BuyerSellProduct, SellRequest
from farmersaccapp.decorators import buyer_required
from products.models import Product


@buyer_required
def buyer_dashboard(request):
    # ✅ Get logged-in user from session
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = get_object_or_404(AllUser, id=user_id)

    # ✅ Get buyer profile
    buyer = get_object_or_404(BuyerProfile, user=user)

    buy_prices = BuyerBuyPrice.objects.filter(buyer=buyer)
    shop_products = BuyerSellProduct.objects.filter(buyer=buyer)
    sell_requests = SellRequest.objects.filter(
        buyer_price__buyer=buyer,
        status="pending"
    )

    context = {
        "buyer": buyer,
        "buy_prices": buy_prices,
        "shop_products": shop_products,
        "sell_requests": sell_requests,
    }

    return render(request, "buyer/buyer_dashboard.html", context)


@buyer_required
def add_buying_price(request):
    # ✅ get logged-in user from session
    user_id = request.session.get("user_id")

    user = get_object_or_404(AllUser, id=user_id, role="buyer")

    # ✅ get BuyerProfile
    buyer = get_object_or_404(BuyerProfile, user=user)

    if request.method == "POST":
        BuyerBuyPrice.objects.create(
            buyer=buyer,  # ✅ BuyerProfile
            product_id=request.POST["product"],
            price_per_unit=request.POST["price"],
            unit=request.POST["unit"],
            min_quantity=request.POST["min_quantity"],
        )
        return redirect("buyer_dashboard")

    products = Product.objects.filter(is_active=True)
    return render(request, "buyer/add_buying_price.html", {
        "products": products
    })

@buyer_required
def edit_buying_price(request, price_id):
    user_id = request.session.get("user_id")
    user = get_object_or_404(AllUser, id=user_id, role="buyer")
    buyer = get_object_or_404(BuyerProfile, user=user)

    price = get_object_or_404(BuyerBuyPrice, id=price_id, buyer=buyer)

    if request.method == "POST":
        price.price_per_unit = request.POST["price_per_unit"]
        price.min_quantity = request.POST["min_quantity"]
        price.unit = request.POST["unit"]
        price.save()
        return redirect("buyer_dashboard")

    return render(request, "buyer/edit_buying_price.html", {
        "price": price
    })

@buyer_required
def toggle_buying_price(request, price_id):
    user_id = request.session.get("user_id")
    user = get_object_or_404(AllUser, id=user_id, role="buyer")
    buyer = get_object_or_404(BuyerProfile, user=user)

    price = get_object_or_404(BuyerBuyPrice, id=price_id, buyer=buyer)

    price.is_active = not price.is_active
    price.save()

    return redirect("buyer_dashboard")