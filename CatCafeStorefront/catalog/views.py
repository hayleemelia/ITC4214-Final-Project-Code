from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg
from .models import MenuItem, Category, SubCategory, Tag
from reviews.models import Rating
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


def menu_list(request):
    items = MenuItem.objects.filter(is_available=True).select_related(
        'category', 'subcategory'
    ).prefetch_related('tags')

    #get filter values from URL query parameters
    q = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    subcategory_id = request.GET.get('subcategory', '')
    tag_id = request.GET.get('tag', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    #search by name/subcategory
    if q:
        items = items.filter(
            Q(name__icontains=q) |
            Q(subcategory__name__icontains=q)
        )

    #filter by category
    if category_id:
        items = items.filter(category_id=category_id)

    #filter by subcategory
    if subcategory_id:
        items = items.filter(subcategory_id=subcategory_id)

    #filter by tag
    if tag_id:
        items = items.filter(tags__id=tag_id)

    #filter by minimum price
    if min_price:
        items = items.filter(price__gte=min_price)

    #filter by maximum price
    if max_price:
        items = items.filter(price__lte=max_price)

    #avoid duplicates when filtering through tags
    items = items.distinct()

    favorite_item_ids = []

    if request.user.is_authenticated:
        favorite_item_ids = list(
            request.user.favorites.values_list('id', flat=True)
        )

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
        'favorite_item_ids': favorite_item_ids,
    }

    return render(request, 'catalog/menu_list.html', context)

def item_detail(request, slug):
    item = get_object_or_404(
        MenuItem.objects.select_related('category', 'subcategory').prefetch_related('tags'),
        slug=slug,
        is_available=True
    )

    user_rating = None
    is_favorited = False

    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(user=request.user, item=item).first()
        is_favorited = request.user.favorites.filter(id=item.id).exists()

    rating_stats = item.ratings.aggregate(avg_rating=Avg('score'))
    average_rating = rating_stats['avg_rating']
    rating_count = item.ratings.count()

    favorite_item_ids = []

    if request.user.is_authenticated:
        favorite_item_ids = list(
            request.user.favorites.values_list('id', flat=True)
        )

    context = {
        'item': item,
        'user_rating': user_rating,
        'average_rating': average_rating,
        'rating_count': rating_count,
        'is_favorited': is_favorited,
    }

    return render(request, 'catalog/item_detail.html', context)

@login_required
def rate_item(request, slug):
    item = get_object_or_404(MenuItem, slug=slug, is_available=True)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

    score = request.POST.get('score')

    if not score or not score.isdigit():
        return JsonResponse({'success': False, 'error': 'Invalid rating.'}, status=400)

    score = int(score)

    if not 1 <= score <= 5:
        return JsonResponse({'success': False, 'error': 'Rating must be between 1 and 5.'}, status=400)

    Rating.objects.update_or_create(
        user=request.user,
        item=item,
        defaults={'score': score}
    )

    rating_stats = item.ratings.aggregate(avg_rating=Avg('score'))
    average_rating = rating_stats['avg_rating']
    rating_count = item.ratings.count()

    return JsonResponse({
        'success': True,
        'average_rating': round(average_rating, 1) if average_rating is not None else None,
        'rating_count': rating_count,
        'user_rating': score,
    })

@login_required
def toggle_favorite(request, slug):
    item = get_object_or_404(MenuItem, slug=slug, is_available=True)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

    if request.user.favorites.filter(id=item.id).exists():
        request.user.favorites.remove(item)
        is_favorited = False
    else:
        request.user.favorites.add(item)
        is_favorited = True

    favorites_count = request.user.favorites.count()

    return JsonResponse({
        'success': True,
        'is_favorited': is_favorited,
        'favorites_count': favorites_count,
    })