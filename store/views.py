from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import timedelta
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import Order, OrderItem
from django.http import HttpResponseBadRequest
from django.contrib import messages
from .models import Product, Wishlist
from .cart import Cart
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from .models import UserProfile, Order
from .forms import UserUpdateForm, ProfileUpdateForm



def frange(start, stop, step):
    while start < stop:
        yield round(start, 1)
        start += step


# ✅ Home Page
def home(request):
    one_week_ago = timezone.now() - timedelta(days=7)

    top_sellers = (
        OrderItem.objects
        .filter(order__created_at__gte=one_week_ago)
        .values('product')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:3]
    )

    bestsellers = []
    for item in top_sellers:
        product = Product.objects.get(id=item['product'])
        bestsellers.append({
            'product': product,
            'total_sold': item['total_sold']
        })

    return render(request, 'store/home.html', {
        'bestsellers': bestsellers,
        'topwear': Product.objects.filter(category='Topwear')[:3],
        'bottomwear': Product.objects.filter(category='Bottomwear')[:3],
        'shoes': Product.objects.filter(category='Shoes')[:3],
        'accessories': Product.objects.filter(category='Accessories')[:3],
    })


# ✅ Register (custom with name + email)
def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=email).exists():
            messages.error(request, "User already exists.")
            return redirect('register')

        user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
        login(request, user)
        messages.success(request, "Account successfully registered.")
        return redirect('home')

    return render(request, 'store/register.html')


# ✅ Login (custom using email field)
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # Your form must use name="email"
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'store/login.html')


# ✅ Logout
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')


# ✅ Product Detail
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.category == 'Shoes':
        sizes = [f"{x:.1f}" for x in list(frange(36, 46.5, 0.5))]
    else:
        sizes = ['S', 'M', 'L', 'XL']

    return render(request, 'store/product_detail.html', {
        'product': product,
        'sizes': sizes
    })


# ✅ Add to Cart
def add_to_cart(request, product_id):
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method.")

    product = get_object_or_404(Product, id=product_id)
    size = request.POST.get('size')

    # If the product is not an accessory and size is missing, return error
    if product.category != "Accessories" and not size:
        messages.error(request, "Please select a size.")
        return redirect('product_detail', product_id=product.id)

    # If it's an accessory and size wasn't provided, default to 'One Size'
    if product.category == "Accessories":
        size = size or "One Size"

    cart = Cart(request)
    cart.add(product, size)

    messages.success(request, f"{product.name} (Size: {size}) was added to your cart.")
    return redirect('cart')


# ✅ View Cart
def cart_view(request):
    cart = Cart(request)
    items = cart.get_items()
    return render(request, 'store/cart.html', {'cart_items': items})


# ✅ Remove from Cart
def remove_from_cart(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    return redirect('cart')


# ✅ Add to Wishlist
@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('wishlist')

def remove_from_wishlist(request, product_id):
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    messages.success(request, "Item removed from your wishlist.")
    return redirect('wishlist')


# ✅ View Wishlist
@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user)
    return render(request, 'store/wishlist.html', {'items': items})


def checkout(request):
    cart = Cart(request)
    cart_items = cart.get_items()
    total = sum(item['total_price'] for item in cart_items)

    if request.method == 'POST':
        delivery_address = request.POST.get('delivery_address')
        card_number = request.POST.get('card_number')  # dummy

        # ✅ Create Order
        order = Order.objects.create(
            user=request.user,
            delivery_address=delivery_address,
            total_price=total

        )

        # ✅ Create OrderItems
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                size=item['size'],
                price=item['product'].price
            )

        cart.clear()
        return redirect('order_confirmation', order_id=order.id)

    return render(request, 'store/checkout.html', {
        'cart_items': cart_items,
        'total': total
    })


from .models import Order, OrderItem

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'store/order_confirmation.html', {
        'order': order,
        'order_items': order_items
    })




# ✅ Simple Pages
def topwear(request):
    products = Product.objects.filter(category='Topwear')
    return render(request, 'store/topwear.html', {'products': products})

def bottomwear(request):
    products = Product.objects.filter(category='Bottomwear')
    return render(request, 'store/bottomwear.html', {'products': products})

def shoes(request):
    shoes_products = Product.objects.filter(category='Shoes')
    return render(request, 'store/shoes.html', {'products': shoes_products})


def accessories(request):
    accessories_products = Product.objects.filter(category='Accessories')
    return render(request, 'store/accessories.html', {'products': accessories_products})



@login_required
def bestsellers(request):
    one_week_ago = timezone.now() - timedelta(days=7)

    top_products = (
        OrderItem.objects
        .filter(order__created_at__gte=one_week_ago)
        .values('product')  # group by product
        .annotate(total_sold=Sum('quantity'))  # sum quantities
        .order_by('-total_sold')[:10]
    )

    # Build list of products with quantity
    product_data = []
    for item in top_products:
        product = Product.objects.get(id=item['product'])
        product_data.append({
            'product': product,
            'total_sold': item['total_sold']
        })

    return render(request, 'store/bestsellers.html', {'product_data': product_data})


@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was updated successfully.')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    orders = Order.objects.filter(user=request.user).order_by('-id')
    return render(request, 'store/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'orders': orders
    })


    


