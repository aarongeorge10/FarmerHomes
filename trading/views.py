from django.shortcuts import render, redirect, get_object_or_404
from farmersaccapp.decorators import farmer_required, buyer_required
from buyersapp.models import BuyerBuyPrice
from .models import MarketCart, MarketCartItem, MarketSellOrder, MarketSellOrderItem
from farmersaccapp.models import AllUser, BuyerProfile
from django.http import HttpResponseRedirect
from trading.models import MarketCartItem

from django.http import HttpResponse
from django.core.files import File
from io import BytesIO
import qrcode
from markets.utils import haversine
from trading.models import FarmerNotification


@farmer_required
def add_to_market_cart(request, price_id):
    buyer_price = get_object_or_404(BuyerBuyPrice, id=price_id)
    farmer = request.current_user.farmer_profile
    buyer = buyer_price.buyer
    market = buyer_price.market

    cart, _ = MarketCart.objects.get_or_create(
        farmer=farmer,
        market=market,
        buyer=buyer
    )

    MarketCartItem.objects.create(
        cart=cart,
        buyer_price=buyer_price,
        quantity=int(request.POST["quantity"])
    )

    # ✅ Stay on same page
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


@farmer_required
def view_market_cart(request, cart_id):
    cart = get_object_or_404(
        MarketCart,
        id=cart_id,
        farmer=request.current_user.farmer_profile
    )

    return render(request, "trading/market_cart.html", {
        "cart": cart
    })


@farmer_required
def submit_market_cart(request, cart_id):
    cart = get_object_or_404(
        MarketCart,
        id=cart_id,
        farmer=request.current_user.farmer_profile
    )

    buyer = cart.buyer   # ✅ FIXED

    order = MarketSellOrder.objects.create(
        farmer=cart.farmer,
        buyer=buyer,
        market=cart.market
    )

    for item in cart.items.all():
        MarketSellOrderItem.objects.create(
            order=order,
            product=item.buyer_price.product,
            price_per_unit=item.buyer_price.price_per_unit,
            quantity=item.quantity,
            unit=item.buyer_price.unit
        )

    cart.delete()

    return redirect("nearest_markets")


@buyer_required
def approve_market_order(request, order_id):
    user_id = request.session.get("user_id")
    user = get_object_or_404(AllUser, id=user_id, role="buyer")
    buyer = get_object_or_404(BuyerProfile, user=user)

    order = get_object_or_404(
        MarketSellOrder,
        id=order_id,
        buyer=buyer
    )

    if order.status != "pending":
        return redirect("buyer_market_orders")

    order.status = "approved"
    order.save()

    # 🔔 CREATE FARMER NOTIFICATION (THIS WAS MISSING)
    FarmerNotification.objects.create(
        farmer=order.farmer,
        order=order,
        message=f"Your order #{order.id} has been approved by {buyer.business_name}"
    )

    generate_market_order_qr(order)

    return redirect("buyer_market_orders")


@buyer_required
def reject_market_order(request, order_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    user = get_object_or_404(AllUser, id=user_id, role="buyer")
    buyer = get_object_or_404(BuyerProfile, user=user)

    order = get_object_or_404(
        MarketSellOrder,
        id=order_id,
        buyer=buyer
    )

    if order.status != "pending":
        return redirect("buyer_dashboard")

    order.status = "rejected"
    order.save()

    # 🔔 OPTIONAL NOTIFICATION
    FarmerNotification.objects.create(
        farmer=order.farmer,
        order=order,
        message=f"Your order #{order.id} was rejected by {buyer.business_name}"
    )

    return redirect("buyer_dashboard")



def generate_market_order_qr(order):
    data = f"""
Order ID: {order.id}
Farmer: {order.farmer.user.username}
Buyer: {order.buyer.business_name}
Market: {order.market.name}
"""

    for item in order.items.all():
        data += f"\n{item.product.name} - {item.quantity} {item.unit}"

    qr = qrcode.make(data)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    order.qr_code.save(
        f"market_order_{order.id}.png",
        File(buffer),
        save=True
    )

def market_order_qr(request, order_id):
    order = get_object_or_404(MarketSellOrder, id=order_id)

    farmer = order.farmer
    market = order.market

    distance = None
    if farmer.latitude and farmer.longitude and market.latitude and market.longitude:
        distance = round(
            haversine(
                float(farmer.latitude),
                float(farmer.longitude),
                float(market.latitude),
                float(market.longitude)
            ),
            2
        )

    return render(request, "trading/market_order_qr.html", {
        "order": order,
        "farmer": farmer,
        "distance": distance
    })


@buyer_required
def buyer_market_orders(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    user = get_object_or_404(AllUser, id=user_id, role="buyer")
    buyer = get_object_or_404(BuyerProfile, user=user)

    orders = (
        MarketSellOrder.objects
        .filter(buyer=buyer)
        .select_related("farmer", "market")
        .prefetch_related("items")
        .order_by("-created_at")
    )

    return render(request, "trading/buyer_market_orders.html", {
        "orders": orders
    })

@farmer_required
def update_cart_item(request, item_id):
    item = get_object_or_404(
        MarketCartItem,
        id=item_id,
        cart__farmer=request.current_user.farmer_profile
    )

    if request.method == "POST":
        item.quantity = int(request.POST["quantity"])
        item.save()

    return redirect("view_market_cart", item.cart.id)

@farmer_required
def remove_cart_item(request, item_id):
    item = get_object_or_404(
        MarketCartItem,
        id=item_id,
        cart__farmer=request.current_user.farmer_profile
    )

    cart_id = item.cart.id
    item.delete()

    return redirect("view_market_cart", cart_id)

@farmer_required
def my_market_carts(request):
    farmer = request.current_user.farmer_profile

    carts = MarketCart.objects.filter(
        farmer=farmer
    ).select_related("market", "buyer")

    return render(request, "trading/my_market_carts.html", {
        "carts": carts
    })

@buyer_required
def complete_market_order(request, order_id):
    user_id = request.session.get("user_id")
    user = get_object_or_404(AllUser, id=user_id, role="buyer")
    buyer = get_object_or_404(BuyerProfile, user=user)

    order = get_object_or_404(
        MarketSellOrder,
        id=order_id,
        buyer=buyer
    )

    if order.status == "approved":
        order.status = "completed"
        order.save()

    return redirect("buyer_market_orders")


@farmer_required
def farmer_order_history(request):
    farmer = request.current_user.farmer_profile

    orders = (
        MarketSellOrder.objects
        .filter(farmer=farmer)
        .select_related("buyer", "market")
        .prefetch_related("items")
        .order_by("-created_at")
    )

    return render(request, "trading/farmer_order_history.html", {
        "orders": orders
    })



@farmer_required
def mark_notification_read(request, notif_id):
    notif = get_object_or_404(
        FarmerNotification,
        id=notif_id,
        farmer=request.current_user.farmer_profile
    )
    notif.is_read = True
    notif.save()
    return redirect("user_dashboard")