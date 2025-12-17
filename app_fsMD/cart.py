# shop/cart.py
from decimal import Decimal
from .models import Product

CART_SESSION_KEY = "cart"

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, product_id: int, qty: int = 1, replace: bool = False):
        pid = str(product_id)
        qty = max(1, int(qty))

        if pid not in self.cart:
            self.cart[pid] = 0

        if replace:
            self.cart[pid] = qty
        else:
            self.cart[pid] += qty

        self.session.modified = True

    def set(self, product_id: int, qty: int):
        pid = str(product_id)
        qty = max(1, int(qty))
        self.cart[pid] = qty
        self.session.modified = True

    def remove(self, product_id: int):
        pid = str(product_id)
        if pid in self.cart:
            del self.cart[pid]
            self.session.modified = True

    def clear(self):
        self.session.pop(CART_SESSION_KEY, None)
        self.session.modified = True

    def items(self):
        """
        Returns enriched items with Product objects + totals computed from DB.
        """
        product_ids = list(self.cart.keys())
        products = Product.objects.filter(id__in=product_ids)
        products_map = {str(p.id): p for p in products}

        enriched = []
        for pid, qty in self.cart.items():
            p = products_map.get(pid)
            if not p:
                continue
            unit = Decimal(str(p.final_price))  # always compute from DB
            qty_int = int(qty)

            # Optional: clamp to stock
            if hasattr(p, "quantity"):
                qty_int = min(qty_int, max(0, p.quantity))

            enriched.append({
                "product": p,
                "qty": qty_int,
                "unit_price": unit,
                "line_total": unit * qty_int,
            })
        return enriched

    def total_qty(self):
        return sum(int(q) for q in self.cart.values())

    def total_price(self):
        return sum(i["line_total"] for i in self.items())
