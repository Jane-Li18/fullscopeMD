from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify


def category_image_upload_to(instance, filename: str) -> str:
    # If slug isn't set yet, fallback to slugified name
    safe_slug = instance.slug or slugify(instance.name)
    return f"categories/{safe_slug}/{filename}"


def product_main_image_upload_to(instance, filename: str) -> str:
    # If slug isn't set yet, fallback to slugified name
    safe_slug = instance.slug or slugify(instance.name)
    return f"products/{safe_slug}/main/{filename}"


def product_sub_image_upload_to(instance, filename: str) -> str:
    safe_slug = instance.product.slug or slugify(instance.product.name)
    # put sub images directly under the product folder (outside /main)
    return f"products/{safe_slug}/{filename}"


class Category(models.Model):
    class Kind(models.TextChoices):
        PROGRAM = "program", "Program"
        SERVICE = "service", "Service"

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    kind = models.CharField(   # ✅ REQUIRED
        max_length=10,
        choices=Kind.choices,
        default=Kind.PROGRAM,  # existing rows become "Program" automatically
    )

    short_description = models.TextField(blank=True)
    long_description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to=category_image_upload_to,
        blank=True,
        null=True,
    )

    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    class DiscountType(models.TextChoices):
        NONE = "none", "None"
        PERCENT = "percent", "Percent"
        FIXED = "fixed", "Fixed Amount"

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )

    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    # Content sections
    short_details = models.TextField(blank=True)  # Top section (short)
    long_details = models.TextField(blank=True)   # Bottom section (long/clinical)

    # Main product image (fallback to default image if not uploaded)
    main_image = models.ImageField(
        upload_to=product_main_image_upload_to,
        default="products/no_image_available.png",  # put this file in MEDIA_ROOT/products/
        blank=True,
    )

    # Commerce fields
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    quantity = models.PositiveIntegerField(default=0)

    discount_type = models.CharField(
        max_length=10,
        choices=DiscountType.choices,
        default=DiscountType.NONE,
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    is_active = models.BooleanField(default=True)

    requires_prescription = models.BooleanField(default=False)
    requires_consultation = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def clean(self):
        if self.discount_type == self.DiscountType.PERCENT:
            if self.discount_value > Decimal("100.00"):
                raise ValueError("Percent discount cannot exceed 100.")
        elif self.discount_type == self.DiscountType.FIXED:
            if self.discount_value > self.price:
                raise ValueError("Fixed discount cannot exceed product price.")

    @property
    def final_price(self) -> Decimal:
        if self.discount_type == self.DiscountType.PERCENT:
            return max(
                Decimal("0.00"),
                self.price * (Decimal("1.00") - (self.discount_value / Decimal("100.00"))),
            )
        if self.discount_type == self.DiscountType.FIXED:
            return max(Decimal("0.00"), self.price - self.discount_value)
        return self.price

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """
    Optional sub images (gallery)
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to=product_sub_image_upload_to)
    alt_text = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.product.name} - Image #{self.id}"
