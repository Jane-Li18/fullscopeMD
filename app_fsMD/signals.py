from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Category, Product, ProductImage

def bump_site_cache_version():
    key = "site_cache_v"
    try:
        cache.incr(key)
    except Exception:
        cache.set(key, 2, None)

@receiver([post_save, post_delete], sender=Category)
@receiver([post_save, post_delete], sender=Product)
@receiver([post_save, post_delete], sender=ProductImage)
def _bust_cache(sender, **kwargs):
    bump_site_cache_version()
