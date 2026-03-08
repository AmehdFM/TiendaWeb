from django.db import models
from django.utils.text import slugify
from django.db.models import Sum


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
    # stock moved to ProductSize

    # Image URLs instead of files
    image_url_1 = models.URLField(max_length=500)  # Required
    image_url_2 = models.URLField(max_length=500, blank=True, null=True)
    image_url_3 = models.URLField(max_length=500, blank=True, null=True)
    image_url_4 = models.URLField(max_length=500, blank=True, null=True)

    tags = models.ManyToManyField(Tag, related_name='products', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def total_stock(self):
        return sum(item.stock for item in self.sizes.all())


class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    name = models.CharField(max_length=50)  # e.g., 'S', 'M', 'L', '42', '43'
    stock = models.IntegerField(default=0)

    class Meta:
        unique_together = ('product', 'name')
        verbose_name = "Talla de Producto"
        verbose_name_plural = "Tallas de Producto"

    def __str__(self):
        return f"{self.product.name} - {self.name} (Stock: {self.stock})"


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('SALE', 'Venta'),
        ('RESTOCK', 'Reabastecimiento'),
        ('ADJUSTMENT', 'Ajuste Manual'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transactions')
    product_size = models.ForeignKey(ProductSize, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()  # Negative for sales/adjustments down, positive for restock
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        size_info = f" [{self.product_size.name}]" if self.product_size else ""
        return f"{self.type} - {self.product.name}{size_info} ({self.quantity})"


# ─────────────────────────────────────────────────────────────────────────────
# CLIENTES MAYORISTAS
# ─────────────────────────────────────────────────────────────────────────────

class WholesaleClient(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre")
    company = models.CharField(max_length=200, blank=True, verbose_name="Empresa / Negocio")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, verbose_name="Correo")
    address = models.TextField(blank=True, verbose_name="Dirección")
    notes = models.TextField(blank=True, verbose_name="Notas internas")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")

    class Meta:
        verbose_name = "Cliente Mayorista"
        verbose_name_plural = "Clientes Mayoristas"
        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.name}" + (f" ({self.company})" if self.company else "")

    @property
    def total_spent(self):
        result = self.purchases.aggregate(total=Sum('total'))['total']
        return result or 0

    @property
    def purchase_count(self):
        return self.purchases.count()


class WholesalePurchase(models.Model):
    client = models.ForeignKey(WholesaleClient, on_delete=models.CASCADE, related_name='purchases', verbose_name="Cliente")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='wholesale_purchases', verbose_name="Producto")
    product_size = models.ForeignKey(ProductSize, on_delete=models.SET_NULL, null=True, blank=True, related_name='wholesale_purchases', verbose_name="Talla")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario")
    total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    notes = models.TextField(blank=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Compra Mayorista"
        verbose_name_plural = "Compras Mayoristas"
        ordering = ['-date']

    def save(self, *args, **kwargs):
        self.total = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Compra #{self.pk} — {self.client.name}"


# ─────────────────────────────────────────────────────────────────────────────
# TIENDAS FÍSICAS
# ─────────────────────────────────────────────────────────────────────────────

class PhysicalStore(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre de la tienda")
    address = models.TextField(verbose_name="Dirección")
    city = models.CharField(max_length=100, verbose_name="Ciudad")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, verbose_name="Correo")
    description = models.TextField(blank=True, verbose_name="Descripción / Referencia")
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Tienda Física"
        verbose_name_plural = "Tiendas Físicas"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} — {self.city}"

    @property
    def total_assigned_stock(self):
        result = self.inventory.aggregate(total=Sum('quantity'))['total']
        return result or 0

    @property
    def product_count(self):
        return self.inventory.values('product').distinct().count()


class StoreInventory(models.Model):
    store = models.ForeignKey(PhysicalStore, on_delete=models.CASCADE, related_name='inventory', verbose_name="Tienda")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='store_inventory', verbose_name="Producto")
    product_size = models.ForeignKey(ProductSize, on_delete=models.CASCADE, related_name='store_inventory', verbose_name="Talla")
    quantity = models.IntegerField(default=0, verbose_name="Cantidad asignada")

    class Meta:
        unique_together = ('store', 'product_size')
        verbose_name = "Inventario en Tienda"
        verbose_name_plural = "Inventario en Tiendas"

    def __str__(self):
        return f"{self.store.name} | {self.product.name} ({self.product_size.name}) × {self.quantity}"
