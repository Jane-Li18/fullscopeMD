from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import Category, Product
from .cart import Cart


def get_nav_programs():
    return Category.objects.filter(is_active=True).order_by("sort_order", "name")

def get_core_program_categories():
    return (
        Category.objects.filter(is_active=True)
        .annotate(product_count=Count("products", filter=Q(products__is_active=True)))
        .order_by("sort_order", "name")
    )



def base(request):
    return render(request, "base.html", {"nav_programs": get_nav_programs()})


def index(request):
    nav_programs = get_nav_programs()
    categories = get_core_program_categories()

    products = (
        Product.objects.filter(is_active=True, category__is_active=True)
        .select_related("category")
        .order_by("name")
    )

    return render(
        request,
        "index.html",
        {"nav_programs": nav_programs, "categories": categories, "products": products},
    )


def contact(request):
    return render(request, "navbar/contact.html", {"nav_programs": get_nav_programs()})


def about(request):
    return render(request, "components/about.html", {"nav_programs": get_nav_programs()})


def faq(request):
    return render(request, "navbar/faq.html", {"nav_programs": get_nav_programs()})


def blog(request):
    return render(request, "navbar/blog.html", {"nav_programs": get_nav_programs()})


def terms_conditions(request):
    return render(
        request, "legal_compliance/terms_conditions.html", {"nav_programs": get_nav_programs()}
    )


def privacy_policy(request):
    return render(
        request, "legal_compliance/privacy_policy.html", {"nav_programs": get_nav_programs()}
    )


def refund_policy(request):
    return render(
        request, "legal_compliance/refund_policy.html", {"nav_programs": get_nav_programs()}
    )


def telehealth_consent(request):
    return render(
        request, "legal_compliance/telehealth_consent.html", {"nav_programs": get_nav_programs()}
    )


def hipaa_notice(request):
    return render(request, "legal_compliance/hipaa_notice.html", {"nav_programs": get_nav_programs()})


def medical_disclaimer(request):
    return render(
        request, "legal_compliance/medical_disclaimer.html", {"nav_programs": get_nav_programs()}
    )


def accessibility_statement(request):
    return render(
        request, "legal_compliance/accessibility_statement.html", {"nav_programs": get_nav_programs()}
    )


def program_detail(request, slug):
    nav_programs = get_nav_programs()
    category = get_object_or_404(Category, slug=slug, is_active=True)

    products = (
        category.products.filter(is_active=True)
        .select_related("category")
        .prefetch_related("images")
        .order_by("name")
    )

    return render(
        request,
        "navbar/programs.html",
        {"nav_programs": nav_programs, "category": category, "products": products},
    )


def product_detail(request, slug):
    nav_programs = get_nav_programs()

    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related("images"),
        slug=slug,
        is_active=True,
        category__is_active=True,
    )

    related_products = (
        Product.objects.filter(is_active=True, category=product.category, category__is_active=True)
        .exclude(id=product.id)
        .order_by("name")[:12]
    )

    return render(
        request,
        "products/product_detail.html",
        {"nav_programs": nav_programs, "product": product, "related_products": related_products},
    )


# =========================
# CART (session-based)
# =========================

def _clamp_qty_to_stock(product: Product, qty: int) -> int:
    qty = max(1, int(qty))
    # If your Product has quantity (stock), clamp
    if hasattr(product, "quantity") and product.quantity is not None:
        stock = max(0, int(product.quantity))
        # if stock is 0, still keep qty at 1 for UI consistency, but you may want to reject
        if stock > 0:
            qty = min(qty, stock)
    return qty


def _cart_payload(cart: Cart):
    """
    Standard JSON payload for side cart + badge.
    Includes stock and telemedicine flags for the UI.
    """
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

    return {
        "ok": True,
        "items": items,
        "total_qty": cart.total_qty(),
        "total_price": str(cart.total_price()),
    }


@require_POST
def cart_add(request):
    product_id = int(request.POST.get("product_id"))
    qty = int(request.POST.get("qty", 1))

    product = get_object_or_404(Product, id=product_id)

    # Stock guard
    if hasattr(product, "quantity") and product.quantity is not None and int(product.quantity) <= 0:
        return JsonResponse({"ok": False, "error": "Out of stock"}, status=400)

    qty = _clamp_qty_to_stock(product, qty)

    cart = Cart(request)
    cart.add(product_id=product.id, qty=qty, replace=False)

    # Return full payload so sidebar can refresh immediately
    return JsonResponse(_cart_payload(cart))


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


@require_POST
def cart_remove(request):
    product_id = int(request.POST.get("product_id"))

    cart = Cart(request)
    cart.remove(product_id=product_id)
    return JsonResponse(_cart_payload(cart))


def cart_summary(request):
    cart = Cart(request)
    return JsonResponse(_cart_payload(cart))


def cart_page(request):
    cart = Cart(request)
    return render(request, "shop/cart_page.html", {
        "nav_programs": get_nav_programs(),
        "cart_items": cart.items(),
        "cart_total": cart.total_price(),
        "cart_qty": cart.total_qty(),
        "ghl_checkout_url": getattr(settings, "GHL_CHECKOUT_URL", ""),
    })
