class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get("cart")
        if not cart:
            cart = self.session["cart"] = {}
        self.cart = cart

    def add(self, product, size):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": 1, "size": size}
        else:
            self.cart[product_id]["quantity"] += 1
        self.save()

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session.modified = True

    def get_items(self):
        from .models import Product
        items = []
        for product_id, details in self.cart.items():
            try:
                product = Product.objects.get(id=product_id)
                items.append({
                    "product": product,
                    "size": details["size"],
                    "quantity": details["quantity"],
                    "total_price": product.price * details["quantity"]
                })
            except Product.DoesNotExist:
                continue
        return items

    def clear(self):
        self.session["cart"] = {}
        self.save()
