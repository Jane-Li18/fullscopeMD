# app_fsMD/context_processors.py

from django.core.cache import cache
from django.db.models import Count, Q

from .cart import Cart
from .models import Category


# Cache TTLs
TTL_NAV = 60 * 60          # 1 hour
TTL_MARQUEE = 10 * 60      # 10 minutes

# Marquee behavior
MARQUEE_REPEAT = 3


def _site_cache_version() -> int:
    """
    Global cache version key used to invalidate cached template data site-wide.
    Increment `site_cache_v` (or clear cache) whenever categories change.
    """
    return cache.get_or_set("site_cache_v", 1, None)


def cart_context(request):
    cart = Cart(request)
    return {"cart_qty": cart.total_qty()}


def nav_programs(request):
    """
    Navigation programs/services list with active categories and active product counts.
    Cached for performance.
    """
    v = _site_cache_version()
    key = f"{v}:ctx:nav_programs"

    data = cache.get(key)
    if data is None:
        data = list(
            Category.objects.filter(is_active=True)
            .annotate(product_count=Count("products", filter=Q(products__is_active=True)))
            .order_by("sort_order", "name")
        )
        cache.set(key, data, TTL_NAV)

    return {"nav_programs": data}


def marquee_context(request):
    """
    Active categories repeated for marquee looping.
    Safe to include on any page without passing extra view context.
    Cached for performance.
    """
    v = _site_cache_version()
    key = f"{v}:ctx:marquee_categories:r{MARQUEE_REPEAT}"

    data = cache.get(key)
    if data is None:
        base = list(
            Category.objects.filter(is_active=True).order_by("sort_order", "name")
        )
        data = base * MARQUEE_REPEAT
        cache.set(key, data, TTL_MARQUEE)

    return {"marquee_categories": data}
