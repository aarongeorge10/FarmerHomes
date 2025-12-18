from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "category",
            "season",
            "product_type",
            "description",
            "image",
            "price",
            "is_active",
        ]
