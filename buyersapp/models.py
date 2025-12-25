from django.db import models
from farmersaccapp.models import BuyerProfile
from products.models import Product
from farmersaccapp.models import FarmerProfile

class BuyerBuyPrice(models.Model):
    buyer = models.ForeignKey(
        BuyerProfile,
        on_delete=models.CASCADE,
        related_name="buy_prices"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="buyer_prices"
    )

    price_per_unit = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(max_length=20, default="kg")

    min_quantity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} @ {self.price_per_unit} ({self.buyer.business_name})"


class BuyerSellProduct(models.Model):
    buyer = models.ForeignKey(
        BuyerProfile,
        on_delete=models.CASCADE,
        related_name="shop_products"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="sold_by_buyers"
    )

    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=20, default="kg")

    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - ₹{self.price}"



class SellRequest(models.Model):
    farmer = models.ForeignKey(
        FarmerProfile,
        on_delete=models.CASCADE,
        related_name="sell_requests"
    )

    buyer_price = models.ForeignKey(
        BuyerBuyPrice,
        on_delete=models.CASCADE,
        related_name="sell_requests"
    )

    quantity = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=(
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ),
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.farmer.user.username} → {self.buyer_price.product.name}"
