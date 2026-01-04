from django.db import models
from farmersaccapp.models import FarmerProfile, BuyerProfile
from markets.models import Market
from buyersapp.models import BuyerBuyPrice
from products.models import Product


# =========================
# MARKET CART (ONE PER FARMER PER MARKET)
# =========================
class MarketCart(models.Model):
    farmer = models.ForeignKey(
        FarmerProfile,
        on_delete=models.CASCADE,
        related_name="market_carts"
    )
    market = models.ForeignKey(
        Market,
        on_delete=models.CASCADE,
        related_name="market_carts"
    )
    buyer = models.ForeignKey(
        BuyerProfile,
        on_delete=models.CASCADE,
        related_name="market_carts"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("farmer", "market", "buyer")

    def __str__(self):
        return f"{self.farmer.user.username} - {self.market.name} - {self.buyer.business_name}"



# =========================
# CART ITEMS
# =========================
class MarketCartItem(models.Model):
    cart = models.ForeignKey(
        MarketCart,
        on_delete=models.CASCADE,
        related_name="items"
    )
    buyer_price = models.ForeignKey(
        BuyerBuyPrice,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.buyer_price.product.name} x {self.quantity}"


# =========================
# FINAL SELL ORDER
# =========================
class MarketSellOrder(models.Model):
    farmer = models.ForeignKey(
        FarmerProfile,
        on_delete=models.CASCADE
    )
    buyer = models.ForeignKey(
        BuyerProfile,
        on_delete=models.CASCADE
    )
    market = models.ForeignKey(
        Market,
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=20,
        choices=(
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("completed", "Completed"),
            ("rejected", "Rejected"),
        ),
        default="pending"
    )

    qr_code = models.ImageField(
        upload_to="qr_codes/",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.status}"


# =========================
# ORDER ITEMS (SNAPSHOT)
# =========================
class MarketSellOrderItem(models.Model):
    order = models.ForeignKey(
        MarketSellOrder,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price_per_unit = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class FarmerNotification(models.Model):
    farmer = models.ForeignKey(
        FarmerProfile,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    order = models.ForeignKey(
        MarketSellOrder,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message