from django.shortcuts import render, redirect, get_object_or_404
from .models import ProductCategory, Product
from farmersaccapp.decorators import admin_required
from .forms import ProductForm

@admin_required
def admin_products(request):
    products = Product.objects.all()
    return render(request, "admin/products.html", {"products": products})

def product_list(request, category_key):
    category = get_object_or_404(ProductCategory, key=category_key)
    products = Product.objects.filter(
        category=category,
        is_active=True
    )

    return render(request, "products/product_list.html", {
        "category": category,
        "products": products
    })


@admin_required
def admin_add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("admin_products")
    else:
        form = ProductForm()

    return render(request, "admin/product_form.html", {
        "form": form,
        "title": "Add Product"
    })


@admin_required
def admin_edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect("admin_products")
    else:
        form = ProductForm(instance=product)

    return render(request, "admin/product_form.html", {
        "form": form,
        "title": "Edit Product"
    })


@admin_required
def admin_delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect("admin_products")


def product_list(request, category_key):
    category = get_object_or_404(ProductCategory, key=category_key)

    products = Product.objects.filter(
        category=category,
        is_active=True
    )

    return render(request, "products/product_list.html", {
        "category": category,
        "products": products
    })
