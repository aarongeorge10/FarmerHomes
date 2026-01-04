from django.urls import path
from . import views

urlpatterns = [
    path("add-to-cart/<int:price_id>/", views.add_to_market_cart, name="add_to_market_cart"),
    path("cart/<int:cart_id>/", views.view_market_cart, name="view_market_cart"),
    path("cart/<int:cart_id>/submit/", views.submit_market_cart, name="submit_market_cart"),

    # Buyer actions
    path("order/<int:order_id>/approve/", views.approve_market_order, name="approve_market_order"),
    path("order/<int:order_id>/reject/", views.reject_market_order, name="reject_market_order"),

    # QR view
    path("order/<int:order_id>/qr/", views.market_order_qr, name="market_order_qr"),

    path("buyer/orders/", views.buyer_market_orders, name="buyer_market_orders"),

    path("cart-item/<int:item_id>/update/", views.update_cart_item, name="update_cart_item"),
    path("cart-item/<int:item_id>/remove/", views.remove_cart_item, name="remove_cart_item"),
    path("carts/", views.my_market_carts, name="my_market_carts"),
    
    path("order/<int:order_id>/complete/", views.complete_market_order, name="complete_market_order"),

    path("farmer/orders/", views.farmer_order_history, name="farmer_order_history"),
]
