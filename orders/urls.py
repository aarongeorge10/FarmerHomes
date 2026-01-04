from django.urls import path
from . import views

urlpatterns = [
    # 🛒 Cart actions
    path("add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.view_cart, name="view_cart"),

    # ➕➖ Quantity controls
    path("cart/increase/<int:item_id>/", views.increase_qty, name="increase_qty"),
    path("cart/decrease/<int:item_id>/", views.decrease_qty, name="decrease_qty"),

    # ❌ Remove item
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),

    # 💳 Checkout & order
    path("checkout/<int:cart_id>/", views.checkout, name="checkout"),
    path("payment/<int:order_id>/", views.payment_page, name="payment_page"),
    path("payment/success/<int:order_id>/", views.payment_success, name="payment_success"),

    path("invoice/pdf/<int:invoice_id>/", views.download_invoice_pdf, name="invoice_pdf"),

    path("my-orders/", views.farmer_orders, name="farmer_orders"),
]
