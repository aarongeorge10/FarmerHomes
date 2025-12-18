from django.urls import path
from .views import (
    admin_products,
    admin_add_product,
    admin_edit_product,
    admin_delete_product,
    product_list
)

urlpatterns = [
    # 🔒 Admin routes
    path("admin/", admin_products, name="admin_products"),
    path("admin/add/", admin_add_product, name="admin_add_product"),
    path("admin/edit/<int:pk>/", admin_edit_product, name="admin_edit_product"),
    path("admin/delete/<int:pk>/", admin_delete_product, name="admin_delete_product"),

    # 🌱 Farmer routes
    path("<str:category_key>/", product_list, name="product_list"),
]