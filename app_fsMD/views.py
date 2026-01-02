from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import strip_tags
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from .cart import Cart
from .models import BlogPost, Category, CategoryBullet, Feedback, NewsletterSubscription, Product


def _meta_text(*parts, fallback="", max_len=160) -> str:
    txt = " ".join([p for p in parts if p]).strip() or fallback
    txt = strip_tags(txt)
    txt = " ".join(txt.split())
    return txt[:max_len].rstrip()


def robots_txt(request):
    sitemap_url = request.build_absolute_uri("/sitemap.xml")
    lines = [
        "User-agent: *",
        "Disallow: /cart/",
        "Disallow: /cart/add/",
        "Disallow: /cart/update/",
        "Disallow: /cart/remove/",
        "Disallow: /cart/summary/",
        "Disallow: /newsletter/subscribe/",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


TTL_NAV = 60 * 60
TTL_LIST = 5 * 60
TTL_DETAIL = 10 * 60


def _site_cache_version() -> int:
    return cache.get_or_set("site_cache_v", 1, None)


def _ck(prefix: str, *parts) -> str:
    v = _site_cache_version()
    return f"{v}:{prefix}:" + ":".join(str(p) for p in parts)


def cache_get(key: str, ttl: int, builder):
    data = cache.get(key)
    if data is None:
        data = builder()
        cache.set(key, data, ttl)
    return data


def _active_category_bullets_qs():
    return CategoryBullet.objects.filter(is_active=True).order_by("sort_order", "id")


def get_nav_programs():
    key = _ck("nav_programs")
    return cache_get(
        key,
        TTL_NAV,
        lambda: list(
            Category.objects.filter(is_active=True)
            .prefetch_related(Prefetch("bullets", queryset=_active_category_bullets_qs()))
            .order_by("sort_order", "name")
        ),
    )


def get_core_program_categories():
    key = _ck("core_categories")
    return cache_get(
        key,
        TTL_LIST,
        lambda: list(
            Category.objects.filter(is_active=True)
            .annotate(product_count=Count("products", filter=Q(products__is_active=True)))
            .order_by("sort_order", "name")
        ),
    )


def get_home_products():
    key = _ck("home_products")
    return cache_get(
        key,
        TTL_LIST,
        lambda: list(
            Product.objects.filter(is_active=True, category__is_active=True)
            .select_related("category")
            .order_by("name")
        ),
    )


def home(request):
    feedbacks = (
        Feedback.objects.filter(is_active=True)
        .select_related("product")
        .order_by("-created_at")
    )

    home_posts = (
        BlogPost.objects.filter(is_active=True, is_featured_home=True)
        .order_by("sort_order", "-published_at")[:5]
    )
    featured_post = home_posts[0] if home_posts else None

    return render(
        request,
        "home.html",
        {
            "feedbacks": feedbacks,
            "star_range": range(1, 6),
            "nav_programs": get_nav_programs(),
            "categories": get_core_program_categories(),
            "products": get_home_products(),
            "home_posts": home_posts,
            "featured_post": featured_post,
        },
    )


def contact(request):
    return render(request, "navbar/n_cntct.html", {"nav_programs": get_nav_programs()})


def about(request):
    feedbacks = (
        Feedback.objects.filter(is_active=True)
        .select_related("product")
        .order_by("-created_at")
    )

    return render(
        request,
        "navbar/n_about.html",
        {
            "nav_programs": get_nav_programs(),
            "feedbacks": feedbacks,
            "star_range": range(1, 6),
        },
    )


def faqs(request):
    return render(request, "navbar/n_faqs.html", {"nav_programs": get_nav_programs()})


def blgs_updts(request):
    nav_programs = get_nav_programs()
    topic = request.GET.get("topic", "all")
    slug = request.GET.get("slug")

    posts = BlogPost.objects.filter(is_active=True)
    if topic != "all":
        posts = posts.filter(topic=topic)
    posts = posts.order_by("sort_order", "-published_at")

    featured_post = BlogPost.objects.filter(slug=slug, is_active=True).first() if slug else None
    if not featured_post:
        featured_post = posts.filter(is_featured_page=True).first() or posts.first()

    return render(
        request,
        "navbar/n_blgs_updts.html",
        {
            "nav_programs": nav_programs,
            "posts": posts,
            "featured_post": featured_post,
            "active_topic": topic,
        },
    )


def newsletter_subscribe(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        if email:
            sub, created = NewsletterSubscription.objects.get_or_create(email=email)
            if not created and not sub.is_active:
                sub.is_active = True
                sub.unsubscribed_at = None
                sub.save()
    return redirect(request.META.get("HTTP_REFERER", reverse("blgs_updts")))


def terms_conditions(request):
    return render(request, "legal/terms_conditions.html", {"nav_programs": get_nav_programs()})


def privacy_policy(request):
    return render(request, "legal/privacy_policy.html", {"nav_programs": get_nav_programs()})


def refund_policy(request):
    return render(request, "legal/refund_policy.html", {"nav_programs": get_nav_programs()})


def telehealth_consent(request):
    return render(request, "legal/telehealth_consent.html", {"nav_programs": get_nav_programs()})


def hipaa_notice(request):
    return render(request, "legal/hipaa_notice.html", {"nav_programs": get_nav_programs()})


def medical_disclaimer(request):
    return render(request, "legal/medical_disclaimer.html", {"nav_programs": get_nav_programs()})


def accessibility_statement(request):
    return render(request, "legal/accessibility_statement.html", {"nav_programs": get_nav_programs()})


def prgrm_dtls(request, slug):
    nav_programs = get_nav_programs()

    cat_id_key = _ck("category_id", slug)
    category_id = cache_get(
        cat_id_key,
        TTL_DETAIL,
        lambda: Category.objects.values_list("id", flat=True).get(slug=slug, is_active=True),
    )

    category = get_object_or_404(Category, id=category_id, is_active=True)

    prod_key = _ck("category_products", slug)
    products = cache_get(
        prod_key,
        TTL_LIST,
        lambda: list(
            Product.objects.filter(category=category, is_active=True, category__is_active=True)
            .select_related("category")
            .prefetch_related("images")
            .order_by("name")
        ),
    )

    canonical_url = request.build_absolute_uri(reverse("prgrm_dtls", kwargs={"slug": category.slug}))

    meta_description = _meta_text(
        category.tagline,
        category.short_description,
        fallback=f"Clinician-guided {category.name} telehealth with transparent pricing and nationwide delivery.",
        max_len=160,
    )

    og_image = request.build_absolute_uri(category.image.url) if getattr(category, "image", None) else None

    return render(
        request,
        "category/prgrms_dtls.html",
        {
            "nav_programs": nav_programs,
            "category": category,
            "products": products,
            "meta_description": meta_description,
            "canonical_url": canonical_url,
            "og_title": f"{category.name} | FullScopeMD",
            "og_description": meta_description,
            "og_image": og_image,
        },
    )


def prdct_dtls(request, slug):
    nav_programs = get_nav_programs()

    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related("images"),
        slug=slug,
        is_active=True,
        category__is_active=True,
    )

    related_key = _ck("related_products", product.category_id, product.id)
    related_products = cache_get(
        related_key,
        TTL_LIST,
        lambda: list(
            Product.objects.filter(
                is_active=True,
                category__is_active=True,
                category_id=product.category_id,
            )
            .exclude(id=product.id)
            .select_related("category")
            .order_by("name")[:12]
        ),
    )

    canonical_url = request.build_absolute_uri(reverse("prdct_dtls", kwargs={"slug": product.slug}))

    meta_description = _meta_text(
        product.short_details,
        product.long_details,
        fallback=f"Clinician-guided telehealth access for {product.name} with transparent pricing and nationwide delivery.",
        max_len=160,
    )

    og_image = request.build_absolute_uri(product.main_image.url) if getattr(product, "main_image", None) else None

    return render(
        request,
        "category/prdct_dtls.html",
        {
            "nav_programs": nav_programs,
            "product": product,
            "related_products": related_products,
            "meta_description": meta_description,
            "canonical_url": canonical_url,
            "og_title": f"{product.name} | FullScopeMD",
            "og_description": meta_description,
            "og_image": og_image,
        },
    )


def _clamp_qty_to_stock(product: Product, qty: int) -> int:
    qty = max(1, int(qty))
    stock = max(0, int(getattr(product, "quantity", 0) or 0))
    if stock > 0:
        qty = min(qty, stock)
    return qty


def _cart_payload(cart: Cart):
    items = []
    for i in cart.items():
        p = i["product"]
        stock = max(0, int(getattr(p, "quantity", 0) or 0)) or 999999
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


@never_cache
@require_POST
def cart_add(request):
    product_id = int(request.POST.get("product_id"))
    qty = int(request.POST.get("qty", 1))

    product = get_object_or_404(Product, id=product_id, is_active=True, category__is_active=True)
    if int(getattr(product, "quantity", 0) or 0) <= 0:
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

    product = get_object_or_404(Product, id=product_id, is_active=True, category__is_active=True)
    if int(getattr(product, "quantity", 0) or 0) <= 0:
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
    return render(
        request,
        "shop/cart_page.html",
        {
            "nav_programs": get_nav_programs(),
            "cart_items": cart.items(),
            "cart_total": cart.total_price(),
            "cart_qty": cart.total_qty(),
            "ghl_checkout_url": getattr(settings, "GHL_CHECKOUT_URL", ""),
            "meta_robots": "noindex,nofollow",
        },
    )


def prgrms_srvcs(request):
    nav_programs = get_nav_programs()

    key = _ck("prgrms_srvcs_categories")
    categories = cache_get(
        key,
        TTL_LIST,
        lambda: list(
            Category.objects.filter(is_active=True)
            .annotate(product_count=Count("products", filter=Q(products__is_active=True), distinct=True))
            .order_by("sort_order", "name")
        ),
    )

    programs = [c for c in categories if c.kind == Category.Kind.PROGRAM]
    services = [c for c in categories if c.kind == Category.Kind.SERVICE]
    program_slides = [programs[i:i + 3] for i in range(0, len(programs), 3)]

    products_key = _ck("prgrms_srvcs_products")
    products = cache_get(
        products_key,
        TTL_LIST,
        lambda: list(
            Product.objects.filter(is_active=True, category__is_active=True)
            .select_related("category")
            .order_by("name")
        ),
    )

    canonical_url = request.build_absolute_uri(reverse("prgrms_srvcs"))

    meta_description = _meta_text(
        fallback="Explore FullScopeMD programs and services across weight management, peptides, dermatology, hair loss, wellness therapy, and primary care — with clinician-guided telehealth and nationwide delivery.",
        max_len=160,
    )

    return render(
        request,
        "category/prgrms_srvcs.html",
        {
            "nav_programs": nav_programs,
            "categories": categories,
            "products": products,
            "program_slides": program_slides,
            "services": services,
            "active_categories": categories,
            "meta_description": meta_description,
            "canonical_url": canonical_url,
            "og_title": "Programs & Services | FullScopeMD",
            "og_description": meta_description,
        },
    )

def test_404(request):
    return render(request, "404.html", status=404)

def error_404(request, exception=None):
    context = {
        "seo_title": "404 — Page not found",
        "meta_description": "The requested page could not be found.",
        "meta_robots": "noindex,nofollow",
        "meta_googlebot": "noindex,nofollow",
        # optional, if you use these elsewhere
        "og_title": "404 — Page not found",
        "og_description": "The requested page could not be found.",
    }
    return render(request, "404.html", context=context, status=404)