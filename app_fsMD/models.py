from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from django.utils import timezone
from .utils.images import convert_imagefield_to_webp


def category_image_upload_to(instance, filename: str) -> str:
    safe_slug = instance.slug or slugify(instance.name)
    return f"categories/{safe_slug}/{filename}"


def product_main_image_upload_to(instance, filename: str) -> str:
    safe_slug = instance.slug or slugify(instance.name)
    return f"products/{safe_slug}/main/{filename}"


def product_sub_image_upload_to(instance, filename: str) -> str:
    safe_slug = instance.product.slug or slugify(instance.product.name)
    return f"products/{safe_slug}/{filename}"


class Category(models.Model):
    class Kind(models.TextChoices):
        PROGRAM = "program", "Program"
        SERVICE = "service", "Service"

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    kind = models.CharField(
        max_length=10,
        choices=Kind.choices,
        default=Kind.PROGRAM,
    )

    tagline = models.CharField(max_length=160, blank=True)

    short_description = models.TextField(blank=True)
    long_description = models.TextField(blank=True)

    image = models.ImageField(upload_to=category_image_upload_to, blank=True, null=True, max_length=255)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        if not getattr(self, "_skip_webp", False):
            convert_imagefield_to_webp(self, "image", quality=82, max_px=2400)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CategoryBullet(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="bullets",
    )
    text = models.CharField(max_length=220)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.category.name} • {self.text[:40]}"


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

    short_details = models.TextField(blank=True)
    long_details = models.TextField(blank=True)

    main_image = models.ImageField(
        upload_to=product_main_image_upload_to,
        default="products/no_image_available.png",
        blank=True,
        max_length=255,
    )

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

        if not getattr(self, "_skip_webp", False):
            convert_imagefield_to_webp(self, "main_image", quality=82, max_px=2400)

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
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to=product_sub_image_upload_to, max_length=255)
    alt_text = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def save(self, *args, **kwargs):
        if not getattr(self, "_skip_webp", False):
            convert_imagefield_to_webp(self, "image", quality=82, max_px=2400)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - Image #{self.id}"


class Feedback(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feedbacks",
    )
    testimonial = models.TextField()
    image = models.ImageField(upload_to="feedback_images/", max_length=255)
    star_rating = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"

    def save(self, *args, **kwargs):
        if not getattr(self, "_skip_webp", False):
            convert_imagefield_to_webp(self, "image", quality=82, max_px=1600)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


def blog_image_upload_to(instance, filename: str) -> str:
    safe_slug = instance.slug or slugify(instance.title)
    return f"blog/{safe_slug}/{filename}"


class BlogPost(models.Model):
    class Topic(models.TextChoices):
        WEIGHT = "weight", "Weight Management"
        PEPTIDES = "peptides", "Peptide Therapy"
        SKIN = "skin", "Skin Treatments"
        HAIR = "hair", "Hair Health"
        WELLNESS = "wellness", "Wellness Therapy"
        PRIMARY = "primary", "Primary Care"

    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True, blank=True)

    topic = models.CharField(
        max_length=20,
        choices=Topic.choices,
        default=Topic.WEIGHT,
    )

    badge_label = models.CharField(max_length=80, blank=True)

    excerpt = models.TextField(
        help_text="Short teaser used on homepage and blog listing."
    )

    body = models.TextField(
        help_text="Full blog content (HTML or Markdown)."
    )

    main_image = models.ImageField(
        upload_to=blog_image_upload_to,
        help_text="Main hero image for this blog.",
        max_length=255,
    )

    read_time_label = models.CharField(
        max_length=40,
        default="4–6 min read",
        help_text="E.g. '4 min read', '6–8 min read'",
    )

    published_at = models.DateField(default=timezone.now)

    bullet_1 = models.CharField(max_length=200, blank=True)
    bullet_2 = models.CharField(max_length=200, blank=True)
    bullet_3 = models.CharField(max_length=200, blank=True)

    is_featured_home = models.BooleanField(
        default=False,
        help_text="Show in the home 'Latest Health Blogs' section.",
    )
    is_featured_page = models.BooleanField(
        default=False,
        help_text="Use as the main feature card on the Blogs & Updates page.",
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this post everywhere.",
    )

    sort_order = models.PositiveIntegerField(
        default=0,
        help_text="Manual ordering (lower = higher priority).",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "-published_at", "-id"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.badge_label:
            self.badge_label = self.get_topic_display()

        if not getattr(self, "_skip_webp", False):
            convert_imagefield_to_webp(self, "main_image", quality=82, max_px=2400)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email
