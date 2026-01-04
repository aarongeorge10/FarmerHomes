from django.db import models
from farmersaccapp.models import BuyerProfile
from products.models import Product
from farmersaccapp.models import FarmerProfile
from markets.models import Market


class BuyerBuyPrice(models.Model):
    buyer = models.ForeignKey(
        BuyerProfile,
        on_delete=models.CASCADE,
        related_name="buy_prices"
    )

    market = models.ForeignKey(
    Market,
    on_delete=models.CASCADE,
    related_name="buyer_buy_prices"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="buyer_prices"
    )

    price_per_unit = models.DecimalField(max_digits=8, decimal_places=2,default=1)
    unit = models.CharField(max_length=20, default="kg")
    min_quantity = models.PositiveIntegerField(default=1)

    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} @ {self.price_per_unit} ({self.market.name})"



class BuyerSellProduct(models.Model):
    buyer = models.ForeignKey(
        BuyerProfile,
        on_delete=models.CASCADE,
        related_name="shop_products"
    )

    market = models.ForeignKey(
    Market,
    on_delete=models.CASCADE,
    related_name="buyer_sell_products"
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

    def save(self, *args, **kwargs):
    # Auto-disable ONLY when stock is zero
        if self.stock_quantity <= 0:
            self.is_available = False

        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.product.name} - ₹{self.price} ({self.market.name})"




