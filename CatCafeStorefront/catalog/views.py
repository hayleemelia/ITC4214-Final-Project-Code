from django.shortcuts import get_object_or_404, render
from .models import MenuItem


def menu_list(request):
    items = MenuItem.objects.filter(is_available=True).select_related('category', 'subcategory').prefetch_related('tags')
    return render(request, 'catalog/menu_list.html', {'items': items})


def item_detail(request, slug):
    item = get_object_or_404(
        MenuItem.objects.select_related('category', 'subcategory').prefetch_related('tags'),
        slug=slug,
        is_available=True
    )
    return render(request, 'catalog/item_detail.html', {'item': item})