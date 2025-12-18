from django.db import models

class ProductCategory(models.Model):
    key = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=50, help_text="Material icon name")

    def __str__(self):
        return self.name

class Product(models.Model):

    SEASON_CHOICES = [
        ('Kharif', 'Kharif'),
        ('Rabi', 'Rabi'),
        ('Zaid', 'Zaid'),
        ('All', 'All Seasons'),
    ]

    name = models.CharField(max_length=120)
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name="products"
    )

    season = models.CharField(
        max_length=20,
        choices=SEASON_CHOICES,
        default="All"
    )

    product_type = models.CharField(
        max_length=100,
        help_text="Hybrid, Organic, BT, Equipment Type"
    )

    description = models.TextField()
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
