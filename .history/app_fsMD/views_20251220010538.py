from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.core.cache import cache
from django.views.decorators.cache import cache_page, never_cache

from .models import Category, Product
from .cart import Cart


# =========================
# CACHE HELPERS
# =========================

# TTLs (tune as you like)
TTL_NAV = 60 * 60          # 1 hour
TTL_LIST = 5 * 60          # 5 minutes
TTL_DETAIL = 10 * 60       # 10 minutes

def _site_cache_version() -> int:
    # Increment this to invalidate everything at once (see signals below)
    return cache.get_or_set("site_cache_v", 1, None)

def _ck(prefix: str, *parts) -> str:
    v = _site_cache_version()
    return f"{v}:{prefix}:" + ":".join(str(p) for p in parts)


def get_nav_programs():
    key = _ck("nav_programs")
    data = cache.get(key)
    if data is None:
        data = list(Category.objects.filter(is_active=True).order_by("sort_order", "name"))
        cache.set(key, data, TTL_NAV)
    return data


def get_core_program_categories():
    key = _ck("core_categories")
    data = cache.get(key)
    if data is None:
        data = list(
            Category.objects.filter(is_active=True)
            .annotate(product_count=Count("products", filter=Q(products__is_active=True)))
            .order_by("sort_order", "name")
        )
        cache.set(key, data, TTL_LIST)
    return data


# =========================
# PAGES
# =========================

def base(request):
    return render(request, "base.html", {"nav_programs": get_nav_programs()})


MARQUEE_REPEAT = 3  # adjust for smoother loop (e.g., 4 or 5 if needed)

def index(request):
    nav_programs = get_nav_programs()
    categories = get_core_program_categories()

    active_categories = list(
        Category.objects.filter(is_active=True).order_by("sort_order", "name")
    )
    marquee_categories = active_categories * MARQUEE_REPEAT

    key = _ck("index_products")
    products = cache.get(key)
    if products is None:
        products = list(
            Product.objects.filter(is_active=True, category__is_active=True)
            .select_related("category")
            .order_by("name")
        )
        cache.set(key, products, TTL_LIST)

    return render(
        request,
        "index.html",
        {
            "nav_programs": nav_programs,
            "categories": categories,
            "products": products,
            "marquee_categories": marquee_categories,  # ✅ for mrq1.html
        },
    )


@cache_page(60 * 30)  # these are static pages - safe to cache
def contact(request):
    return render(request, "navbar/n_cntct.html", {"nav_programs": get_nav_programs()})


@cache_page(60 * 30)
def about(request):
    active_categories = list(
        Category.objects.filter(is_active=True).order_by("sort_order", "name")
    )
    marquee_categories = active_categories * MARQUEE_REPEAT

    return render(request, "components/about.html", {
        "nav_programs": get_nav_programs(),
        "marquee_categories": marquee_categories,
    })


@cache_page(60 * 30)
def faqs(request):
    return render(request, "navbar/n_faqs.html", {"nav_programs": get_nav_programs()})


@cache_page(60 * 30)
def blgs_updts(request):
    return render(request, "navbar/n_blgs_updts.html", {"nav_programs": get_nav_programs()})


@cache_page(60 * 60)
def terms_conditions(request):
    return render(request, "legal/terms_conditions.html", {"nav_programs": get_nav_programs()})


@cache_page(60 * 60)
def privacy_policy(request):
    return render(request, "legal/privacy_policy.html", {"nav_programs": get_nav_programs()})


@cache_page(60 * 60)
def refund_policy(request):
    return render(request, "legal/refund_policy.html", {"nav_programs": get_nav_programs()})


@cache_page(60 * 60)
def telehealth_consent(request):
    return render(request, "legal/telehealth_consent.html", {"nav_programs": get_nav_programs()})


@cache_page(60 * 60)
def hipaa_notice(request):
    return render(request, "legal/hipaa_notice.html", {"nav_programs": get_nav_programs()})


@cache_page(60 * 60)
def medical_disclaimer(request):
    return render(request, "legal/medical_disclaimer.html", {"nav_programs": get_nav_programs()})


@cache_page(60 * 60)
def accessibility_statement(request):
    return render(request, "legal/accessibility_statement.html", {"nav_programs": get_nav_programs()})


def prgrm_dtls(request, slug):
    nav_programs = get_nav_programs()

    # cache category fetch by slug
    cat_key = _ck("category", slug)
    category = cache.get(cat_key)
    if category is None:
        category = get_object_or_404(Category, slug=slug, is_active=True)
        cache.set(cat_key, category, TTL_DETAIL)

    prod_key = _ck("category_products", slug)
    products = cache.get(prod_key)
    if products is None:
        products = list(
            category.products.filter(is_active=True)
            .select_related("category")
            .prefetch_related("images")
            .order_by("name")
        )
        cache.set(prod_key, products, TTL_LIST)

    return render(
        request,
        "category/prgrms_dtls.html",
        {"nav_programs": nav_programs, "category": category, "products": products},
    )


def prdct_dtls(request, slug):
    nav_programs = get_nav_programs()

    key = _ck("prdct_dtls", slug)
    cached = cache.get(key)
    if cached is None:
        product = get_object_or_404(
            Product.objects.select_related("category").prefetch_related("images"),
            slug=slug,
            is_active=True,
            category__is_active=True,
        )

        related_products = list(
            Product.objects.filter(is_active=True, category=product.category, category__is_active=True)
            .exclude(id=product.id)
            .order_by("name")[:12]
        )

        cached = (product, related_products)
        cache.set(key, cached, TTL_DETAIL)

    product, related_products = cached

    return render(
        request,
        "category/prdct_dtls.html",
        {"nav_programs": nav_programs, "product": product, "related_products": related_products},
    )


# =========================
# CART (never cache)
# =========================

def _clamp_qty_to_stock(product: Product, qty: int) -> int:
    qty = max(1, int(qty))
    if hasattr(product, "quantity") and product.quantity is not None:
        stock = max(0, int(product.quantity))
        if stock > 0:
            qty = min(qty, stock)
    return qty


def _cart_payload(cart: Cart):
    items = []
    for i in cart.items():
        p = i["product"]
        stock = 999999
        if hasattr(p, "quantity") and p.quantity is not None:
            stock = max(0, int(p.quantity))

        items.append(
            {
                "id": p.id,
                "name": p.name,
                "qty": int(i["qty"]),
                "unit_price": str(i["unit_price"]),
                "line_total": str(i["line_total"]),
                "image": p.main_image.url if getattr(p, "main_image", None) else "",
                "requires_prescription": bool(getattr(p, "requires_prescription", False)),
                "requires_consultation": bool(getattr(p, "requires_consultation", False)),
                "stock": stock,
            }
        )

    return {"ok": True, "items": items, "total_qty": cart.total_qty(), "total_price": str(cart.total_price())}


@never_cache
@require_POST
def cart_add(request):
    product_id = int(request.POST.get("product_id"))
    qty = int(request.POST.get("qty", 1))
    product = get_object_or_404(Product, id=product_id)

    if hasattr(product, "quantity") and product.quantity is not None and int(product.quantity) <= 0:
        return JsonResponse({"ok": False, "error": "Out of stock"}, status=400)

    qty = _clamp_qty_to_stock(product, qty)
    cart = Cart(request)
    cart.add(product_id=product.id, qty=qty, replace=False)
    return JsonResponse(_cart_payload(cart))


@never_cache
@require_POST
def cart_update(request):
    product_id = int(request.POST.get("product_id"))
    qty = int(request.POST.get("qty", 1))
    product = get_object_or_404(Product, id=product_id)

    if hasattr(product, "quantity") and product.quantity is not None and int(product.quantity) <= 0:
        return JsonResponse({"ok": False, "error": "Out of stock"}, status=400)

    qty = _clamp_qty_to_stock(product, qty)
    cart = Cart(request)
    cart.set(product_id=product.id, qty=qty)
    return JsonResponse(_cart_payload(cart))


@never_cache
@require_POST
def cart_remove(request):
    product_id = int(request.POST.get("product_id"))
    cart = Cart(request)
    cart.remove(product_id=product_id)
    return JsonResponse(_cart_payload(cart))


@never_cache
def cart_summary(request):
    cart = Cart(request)
    return JsonResponse(_cart_payload(cart))


@never_cache
def cart_page(request):
    cart = Cart(request)
    return render(request, "shop/cart_page.html", {
        "nav_programs": get_nav_programs(),
        "cart_items": cart.items(),
        "cart_total": cart.total_price(),
        "cart_qty": cart.total_qty(),
        "ghl_checkout_url": getattr(settings, "GHL_CHECKOUT_URL", ""),
    })


def prgrms_srvcs(request):
    nav_programs = get_nav_programs()

    categories = (
        Category.objects
        .filter(is_active=True)
        .annotate(product_count=Count("products", filter=Q(products__is_active=True), distinct=True))
        .order_by("sort_order", "name")
    )

    programs = list(categories.filter(kind=Category.Kind.PROGRAM))
    services = categories.filter(kind=Category.Kind.SERVICE)

    program_slides = [programs[i:i+3] for i in range(0, len(programs), 3)]

    products = (
        Product.objects
        .filter(is_active=True, category__is_active=True)   # <-- add this
        .select_related("category")
        .order_by("name")
    )

    return render(request, "category/prgrms_srvcs.html", {
        "nav_programs": nav_programs,          # <-- add this
        "categories": categories,
        "products": products,
        "program_slides": program_slides,
        "services": services,
        "active_categories": categories,
    })
