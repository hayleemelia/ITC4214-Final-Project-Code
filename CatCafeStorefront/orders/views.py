from decimal import Decimal

from django.db.models import Avg
from django.shortcuts import render, redirect, get_object_or_404

from catalog.models import MenuItem, Category, SubCategory, Tag
from catalog.utils import apply_menu_filters
from .forms import CheckoutForm
from .models import Order, OrderItem
from .utils import build_cart_items


def get_cart(request):
    cart = request.session.get('cart', {})

    if not isinstance(cart, dict):
        cart = {}

    return cart


def add_to_cart(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id, is_available=True)
    cart = get_cart(request)

    item_id_str = str(item.id)

    quantity = 1

    if request.method == 'POST':
        submitted_quantity = request.POST.get('quantity')

        if submitted_quantity and submitted_quantity.isdigit():
            quantity = int(submitted_quantity)

            if quantity < 1:
                quantity = 1

    if item_id_str in cart:
        cart[item_id_str] += quantity
    else:
        cart[item_id_str] = quantity

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('orders:cart_detail')


def remove_from_cart(request, item_id):
    cart = get_cart(request)
    item_id_str = str(item_id)

    if item_id_str in cart:
        del cart[item_id_str]

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('orders:cart_detail')


def update_cart_quantity(request, item_id):
    cart = get_cart(request)
    item_id_str = str(item_id)

    if request.method == 'POST':
        quantity = request.POST.get('quantity')

        if quantity and quantity.isdigit():
            quantity = int(quantity)

            if quantity > 0:
                cart[item_id_str] = quantity
            else:
                cart.pop(item_id_str, None)

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('orders:cart_detail')


def cart_detail(request):
    cart = get_cart(request)
    cart_items, total = build_cart_items(cart)

    context = {
        'cart_items': cart_items,
        'total': total,
    }

    return render(request, 'orders/cart.html', context)

def checkout(request):
    cart = get_cart(request)

    if not cart:
        return redirect('orders:cart_detail')

    cart_items, total = build_cart_items(cart)

    if not cart_items:
        request.session['cart'] = {}
        request.session.modified = True
        return redirect('orders:cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)

        if form.is_valid():
            card_number = form.cleaned_data['card_number']

            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                billing_address=form.cleaned_data['billing_address'],
                card_last_four=card_number[-4:],
                total=total,
            )

            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    menu_item=cart_item['item'],
                    quantity=cart_item['quantity'],
                    price_at_purchase=cart_item['item'].price,
                )

            request.session['cart'] = {}
            request.session.modified = True

            return redirect('orders:order_confirmed', order_id=order.id)
    else:
        initial_data = {}

        if request.user.is_authenticated:
            initial_data = {
                'full_name': f"{request.user.first_name} {request.user.last_name}".strip(),
                'email': request.user.email,
            }

        form = CheckoutForm(initial=initial_data)

    context = {
        'form': form,
        'cart_items': cart_items,
        'total': total,
    }

    return render(request, 'orders/checkout.html', context)


def order_confirmed(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    return render(request, 'orders/order_confirmed.html', {
        'order': order
    })

def order_now(request):
    items = MenuItem.objects.filter(is_available=True).annotate(
        avg_rating=Avg('ratings__score')
    ).select_related('category', 'subcategory').prefetch_related('tags')

    items, current_filters = apply_menu_filters(request, items)

    beverages = items.filter(category__name__iexact='beverages')
    desserts = items.filter(category__name__iexact='desserts')

    context = {
        'beverages': beverages,
        'desserts': desserts,
        'categories': Category.objects.all(),
        'subcategories': SubCategory.objects.all(),
        'tags': Tag.objects.all(),
        **current_filters,
    }

    return render(request, 'orders/order_now.html', context)