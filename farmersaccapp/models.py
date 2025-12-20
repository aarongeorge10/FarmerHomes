# accounts/models.py
from django.db import models
from django.utils import timezone

class AllUser(models.Model):
    ROLE_CHOICES = (
        ('farmer', 'Farmer'),
        ('buyer', 'Buyer / Wholesaler / Exporter'),
        ('admin', 'Admin'),
    )

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

            # 🔐 Forgot password fields
    reset_token = models.CharField(max_length=100, null=True, blank=True)
    reset_token_created = models.DateTimeField(null=True, blank=True)

    # 🔹 Buyer specific
    shop_name = models.CharField(max_length=200, blank=True, null=True)
    gst_number = models.CharField(max_length=20, blank=True, null=True)

    # 🔹 Approval system
    is_approved = models.BooleanField(default=False)

    rejection_reason = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.username} ({self.role})"


class FarmerProfile(models.Model):
    user = models.OneToOneField(
        AllUser,
        on_delete=models.CASCADE,
        related_name='farmer_profile'
    )

    village = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)

    soil_type = models.CharField(max_length=100, blank=True, null=True)
    farm_area_acres = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    bank_account_number = models.CharField(max_length=30, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Farmer: {self.user.username}"


class BuyerProfile(models.Model):
    user = models.OneToOneField(
        AllUser,
        on_delete=models.CASCADE,
        related_name='buyer_profile'
    )

    business_name = models.CharField(max_length=150, blank=True, null=True)
    gst_number = models.CharField(max_length=30, blank=True, null=True)
    is_exporter = models.BooleanField(default=False)

    def __str__(self):
        return f"Buyer: {self.user.username}"


class Wallet(models.Model):
    user = models.OneToOneField(
        AllUser,
        on_delete=models.CASCADE,
        related_name='wallet'
    )

    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Wallet - ₹{self.balance}"




from django.db import models

# -------------------------
# Product Category
# -------------------------
class ProductCategory(models.Model):
    name = models.CharField(max_length=100)  # Seeds, Fertilizers, Equipment
    icon = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name


# -------------------------
# Base Product
# -------------------------
class Product(models.Model):
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name="products"
    )

    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    image = models.ImageField(upload_to="products/")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"


# -------------------------
# Seed Details
# -------------------------
class SeedDetail(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    crop_type = models.CharField(max_length=100)
    soil_type = models.CharField(max_length=100)
    season = models.CharField(max_length=50)

    def __str__(self):
        return self.product.name


# -------------------------
# Fertilizer Details
# -------------------------
class FertilizerDetail(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    nutrient_type = models.CharField(max_length=100)  # NPK
    usage_instructions = models.TextField()

    def __str__(self):
        return self.product.name


# -------------------------
# Equipment / Tool Details
# -------------------------
class EquipmentDetail(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    is_rentable = models.BooleanField(default=False)
    power_type = models.CharField(max_length=100)  # Manual / Electric / Diesel

    def __str__(self):
        return self.product.name
