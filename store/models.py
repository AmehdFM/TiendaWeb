from django.db import models
from django.utils.text import slugify

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    icon_url = models.URLField(max_length=500, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    
    # Image URLs instead of files
    image_url_1 = models.URLField(max_length=500) # Required
    image_url_2 = models.URLField(max_length=500, blank=True, null=True)
    image_url_3 = models.URLField(max_length=500, blank=True, null=True)
    image_url_4 = models.URLField(max_length=500, blank=True, null=True)
    
    tags = models.ManyToManyField(Tag, related_name='products', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('SALE', 'Venta'),
        ('RESTOCK', 'Reabastecimiento'),
        ('ADJUSTMENT', 'Ajuste Manual'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField() # Negative for sales/adjustments down, positive for restock
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.product.name} ({self.quantity})"
