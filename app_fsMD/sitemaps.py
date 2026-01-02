from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Category, Product, BlogPost

class StaticViewSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return [
            "home",
            "about",
            "contact",
            "faqs",
            "prgrms_srvcs",
            "blgs_updts",
            "terms_conditions",
            "privacy_policy",
            "refund_policy",
            "telehealth_consent",
            "hipaa_notice",
            "medical_disclaimer",
            "accessibility_statement",
        ]

    def location(self, item):
        return reverse(item)

class CategorySitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return Category.objects.filter(is_active=True)

    def location(self, obj):
        return reverse("prgrm_dtls", kwargs={"slug": obj.slug})

class ProductSitemap(Sitemap):
    priority = 0.9
    changefreq = "weekly"

    def items(self):
        return Product.objects.filter(is_active=True, category__is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse("prdct_dtls", kwargs={"slug": obj.slug})

class BlogSitemap(Sitemap):
    priority = 0.6
    changefreq = "monthly"

    def items(self):
        return BlogPost.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse("blgs_updts")
