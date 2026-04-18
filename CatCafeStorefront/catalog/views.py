from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg
from .models import MenuItem, Category, SubCategory, Tag
from reviews.models import Rating
from django.contrib.auth.decorators import login_required

def menu_list(request):
    items = MenuItem.objects.filter(is_available=True).select_related(
        'category', 'subcategory'
    ).prefetch_related('tags')

    # Get filter values from URL query parameters
    q = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    subcategory_id = request.GET.get('subcategory', '')
    tag_id = request.GET.get('tag', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    # Search by name/subcategory
    if q:
        items = items.filter(
            Q(name__icontains=q) |
            Q(subcategory__name__icontains=q)
        )

    # Filter by category
    if category_id:
        items = items.filter(category_id=category_id)

    # Filter by subcategory
    if subcategory_id:
        items = items.filter(subcategory_id=subcategory_id)

    # Filter by tag
    if tag_id:
        items = items.filter(tags__id=tag_id)

    # Filter by minimum price
    if min_price:
        items = items.filter(price__gte=min_price)

    # Filter by maximum price
    if max_price:
        items = items.filter(price__lte=max_price)

    # Avoid duplicates when filtering through tags
    items = items.distinct()

    context = {
        'items': items,
        'categories': Category.objects.all(),
        'subcategories': SubCategory.objects.all(),
        'tags': Tag.objects.all(),

        # send current values back so the form stays filled in
        'current_q': q,
        'current_category': category_id,
        'current_subcategory': subcategory_id,
        'current_tag': tag_id,
        'current_min_price': min_price,
        'current_max_price': max_price,
    }

    return render(request, 'catalog/menu_list.html', context)

def item_detail(request, slug):
    item = get_object_or_404(
        MenuItem.objects.select_related('category', 'subcategory').prefetch_related('tags'),
        slug=slug,
        is_available=True
    )

    user_rating = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(user=request.user, item=item).first()

    rating_stats = item.ratings.aggregate(avg_rating=Avg('score'))
    average_rating = rating_stats['avg_rating']
    rating_count = item.ratings.count()

    context = {
        'item': item,
        'user_rating': user_rating,
        'average_rating': average_rating,
        'rating_count': rating_count,
    }

    return render(request, 'catalog/item_detail.html', context)

@login_required
def rate_item(request, slug):
    item = get_object_or_404(MenuItem, slug=slug, is_available=True)

    if request.method == 'POST':
        score = request.POST.get('score')

        if score and score.isdigit():
            score = int(score)

            if 1 <= score <= 5:
                Rating.objects.update_or_create(
                    user=request.user,
                    item=item,
                    defaults={'score': score}
                )

    return redirect('catalog:item_detail', slug=item.slug)