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

    # 📍 GEO LOCATION (RECOMMENDED)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    soil_type = models.CharField(max_length=100, blank=True, null=True)
    farm_area_acres = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    bank_account_number = models.CharField(max_length=14, blank=True, null=True)
    ifsc_code = models.CharField(max_length=11, blank=True, null=True)

    def __str__(self):
        return self.user.username



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

