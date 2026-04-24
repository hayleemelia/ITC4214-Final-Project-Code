from django.db.models import Q


def apply_menu_filters(request, items):
    q = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    subcategory_id = request.GET.get('subcategory', '')
    tag_id = request.GET.get('tag', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    if q:
        items = items.filter(
            Q(name__icontains=q) |
            Q(subcategory__name__icontains=q)
        )

    if category_id:
        items = items.filter(category_id=category_id)

    if subcategory_id:
        items = items.filter(subcategory_id=subcategory_id)

    if tag_id:
        items = items.filter(tags__id=tag_id)

    if min_price:
        items = items.filter(price__gte=min_price)

    if max_price:
        items = items.filter(price__lte=max_price)

    current_filters = {
        'current_q': q,
        'current_category': category_id,
        'current_subcategory': subcategory_id,
        'current_tag': tag_id,
        'current_min_price': min_price,
        'current_max_price': max_price,
    }

    return items.distinct(), current_filters