from .cart import Cart
from django.db.models import Count, Q
from .models import Category

def cart_context(request):
    cart = Cart(request)
    return {"cart_qty": cart.total_qty()}

def nav_programs(request):
    return {
        "nav_programs": (
            Category.objects.filter(is_active=True)
            .annotate(product_count=Count("products", filter=Q(products__is_active=True)))
            .order_by("sort_order", "name")
        )
    }
