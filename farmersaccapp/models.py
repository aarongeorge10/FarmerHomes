# farmersaccapp/models.py
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

    CROP_CHOICES = (

        # 🌾 CEREALS
        ("rice", "Rice"),
        ("wheat", "Wheat"),
        ("maize", "Maize"),
        ("barley", "Barley"),
        ("oats", "Oats"),
        ("sorghum", "Sorghum (Jowar)"),
        ("millet", "Millet (Bajra)"),
        ("ragi", "Ragi"),

        # 🌱 PULSES
        ("gram", "Chickpea (Gram)"),
        ("pigeon_pea", "Pigeon Pea (Toor Dal)"),
        ("lentil", "Lentil (Masoor)"),
        ("mung", "Green Gram (Moong)"),
        ("urad", "Black Gram (Urad)"),
        ("pea", "Pea"),

        # 🌻 OILSEEDS
        ("mustard", "Mustard"),
        ("groundnut", "Groundnut"),
        ("sunflower", "Sunflower"),
        ("soybean", "Soybean"),
        ("sesame", "Sesame (Til)"),
        ("castor", "Castor"),

        # 🌿 FIBER
        ("cotton", "Cotton"),
        ("jute", "Jute"),

        # 🌴 CASH CROPS
        ("sugarcane", "Sugarcane"),
        ("tobacco", "Tobacco"),

        # 🥬 VEGETABLES
        ("potato", "Potato"),
        ("onion", "Onion"),
        ("tomato", "Tomato"),
        ("chilli", "Chilli"),
        ("cabbage", "Cabbage"),
        ("cauliflower", "Cauliflower"),
        ("brinjal", "Brinjal"),
        ("okra", "Okra"),

        # 🍎 FRUITS
        ("banana", "Banana"),
        ("mango", "Mango"),
        ("grapes", "Grapes"),
        ("orange", "Orange"),
        ("pomegranate", "Pomegranate"),
        ("apple", "Apple"),
        ("papaya", "Papaya"),
    )

    user = models.OneToOneField(
        AllUser,
        on_delete=models.CASCADE,
        related_name="farmer_profile"
    )

    village = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)

    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    soil_type = models.CharField(max_length=100, blank=True, null=True)
    farm_area_acres = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    bank_account_number = models.CharField(max_length=14, blank=True, null=True)
    ifsc_code = models.CharField(max_length=11, blank=True, null=True)

    # 🌾 NEW FIELD – Main crop grown
    crop = models.CharField(
        max_length=30,
        choices=CROP_CHOICES,
        blank=True,
        null=True
    )

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


class FarmerReport(models.Model):
    STATUS_CHOICES = (
        ("open", "Open"),
        ("resolved", "Resolved"),
    )

    farmer = models.ForeignKey(
        FarmerProfile,
        on_delete=models.CASCADE,
        related_name="reports"
    )

    subject = models.CharField(max_length=200)
    message = models.TextField()

    admin_reply = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.farmer.user.username} - {self.subject}"