from django.contrib import admin
from .models import (
    Category,
    CategoryBullet,
    Product,
    ProductImage,
    Feedback,
    BlogPost,
    NewsletterSubscription,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "quantity", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]


class CategoryBulletInline(admin.TabularInline):
    model = CategoryBullet
    extra = 1
    fields = ("text", "sort_order", "is_active")
    ordering = ("sort_order", "id")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "is_active", "sort_order")
    list_filter = ("kind", "is_active")
    search_fields = ("name", "tagline", "short_description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CategoryBulletInline]


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "star_rating",
        "testimonial",
        "is_active",
    )
    list_filter = ("star_rating", "is_active")
    search_fields = ("first_name", "last_name", "email")
    ordering = ("-star_rating",)
    list_editable = ("is_active",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset


# =========================
# BLOG / NEWSLETTER ADMIN
# =========================

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "topic",
        "badge_label",
        "published_at",
        "is_featured_home",
        "is_featured_page",
        "is_active",
        "sort_order",
    )
    list_filter = (
        "topic",
        "is_active",
        "is_featured_home",
        "is_featured_page",
    )
    search_fields = (
        "title",
        "slug",
        "excerpt",
        "body",
    )
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    ordering = ("sort_order", "-published_at")
    list_editable = (
        "is_featured_home",
        "is_featured_page",
        "is_active",
        "sort_order",
    )
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            "fields": (
                "title",
                "slug",
                "topic",
                "badge_label",
                "excerpt",
                "body",
            ),
        }),
        ("Media", {
            "fields": ("main_image",),
        }),
        ("Display & Meta", {
            "fields": (
                "read_time_label",
                "published_at",
                "is_featured_home",
                "is_featured_page",
                "is_active",
                "sort_order",
            ),
        }),
        ("Feature bullets (optional)", {
            "fields": ("bullet_1", "bullet_2", "bullet_3"),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "created_at", "unsubscribed_at")
    list_filter = ("is_active",)
    search_fields = ("email",)
    readonly_fields = ("created_at", "unsubscribed_at")
    ordering = ("-created_at",)
