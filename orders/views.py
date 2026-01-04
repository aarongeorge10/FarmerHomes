from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem, Order, OrderItem
from buyersapp.models import BuyerSellProduct
from markets.models import Market
from farmersaccapp.decorators import farmer_required
from django.contrib import messages
import uuid
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from .models import Invoice



# Create your views here.

@farmer_required
def add_to_cart(request, product_id):
    if request.method != "POST":
        return redirect(request.META.get("HTTP_REFERER"))

    user = request.current_user

    product = get_object_or_404(
        BuyerSellProduct,
        id=product_id,
        is_available=True
    )

    # ✅ ONE CART PER MARKET
    cart, _ = Cart.objects.get_or_create(
        farmer=user,
        market=product.market,
        is_active=True
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += 1
    cart_item.save()

    # 🛒 update cart count (ALL carts combined)
    total_items = CartItem.objects.filter(
        cart__farmer=user,
        cart__is_active=True
    ).count()

    request.session["cart_count"] = total_items

    return redirect(request.META.get("HTTP_REFERER"))



@farmer_required
def view_cart(request):
    user = request.current_user

    carts = Cart.objects.filter(
        farmer=user,
        is_active=True
    ).prefetch_related("items__product__buyer", "items__product__market")

    return render(request, "orders/cart.html", {
        "carts": carts
    })


@farmer_required
def checkout(request, cart_id):
    user = request.current_user

    cart = get_object_or_404(
        Cart,
        id=cart_id,
        farmer=user,
        is_active=True
    )

    # 🟢 Create order (NO stock change here)
    order = Order.objects.create(
        farmer=user,
        market=cart.market,
        total_price=cart.total_amount()
    )

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    # ❗ DO NOT reduce stock
    # ❗ DO NOT close cart

    return redirect("payment_page", order.id)


@farmer_required
def increase_qty(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__farmer=request.current_user,
        cart__is_active=True
    )
    item.quantity += 1
    item.save()
    return redirect("view_cart")


@farmer_required
def decrease_qty(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect("view_cart")


@farmer_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect("view_cart")



@farmer_required
def payment_page(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        farmer=request.current_user
    )

    return render(request, "orders/payment.html", {
        "order": order
    })


@farmer_required
def payment_success(request, order_id):
    user = request.current_user

    order = get_object_or_404(
        Order,
        id=order_id,
        farmer=user
    )

    # ✅ UPDATE ORDER STATUS
    order.status = "paid"
    order.save()

    # 🧾 Create invoice
    invoice = Invoice.objects.create(
        order=order,
        invoice_number=f"INV-{uuid.uuid4().hex[:10].upper()}",
        total_amount=order.total_price,
        payment_status="paid",
        payment_method="UPI"
    )

    # 🔻 Reduce stock
    for item in order.items.all():
        product = item.product
        product.stock_quantity -= item.quantity
        if product.stock_quantity <= 0:
            product.is_available = False
        product.save()

    # ❌ Close cart
    Cart.objects.filter(
        farmer=user,
        market=order.market,
        is_active=True
    ).update(is_active=False)

    # 🔄 Update cart badge
    request.session["cart_count"] = CartItem.objects.filter(
        cart__farmer=user,
        cart__is_active=True
    ).count()

    return render(request, "orders/invoice.html", {
        "order": order,
        "invoice": invoice
    })


@farmer_required
def download_invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(
        Invoice,
        id=invoice_id,
        order__farmer=request.current_user
    )

    order = invoice.order

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{invoice.invoice_number}.pdf"'
    )

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 50

    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "Farmer Homes - Invoice")
    y -= 30

    p.setFont("Helvetica", 10)
    p.drawString(50, y, f"Invoice No: {invoice.invoice_number}")
    y -= 15
    p.drawString(50, y, f"Market: {order.market.name}")
    y -= 15
    p.drawString(50, y, f"Total Paid: ₹{invoice.total_amount}")
    y -= 30

    # Table header
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "Product")
    p.drawString(300, y, "Qty")
    p.drawString(350, y, "Price")
    y -= 15

    p.setFont("Helvetica", 10)
    for item in order.items.all():
        p.drawString(50, y, item.product.product.name)
        p.drawString(300, y, str(item.quantity))
        p.drawString(350, y, f"₹{item.price}")
        y -= 15

    y -= 20
    p.drawString(50, y, "Thank you for shopping with Farmer Homes 🌾")

    p.showPage()
    p.save()

    return response

@farmer_required
def farmer_orders(request):
    orders = (
        Order.objects
        .filter(farmer=request.current_user)
        .select_related("market")
        .prefetch_related("items", "invoice")
        .order_by("-created_at")
    )

    return render(request, "orders/farmer_orders.html", {
        "orders": orders
    })