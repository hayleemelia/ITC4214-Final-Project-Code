from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg
from .models import MenuItem, Category, SubCategory, Tag
from reviews.models import Rating
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from .forms import MenuItemForm, CategoryForm, SubCategoryForm


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

    #recommendation system

    #current item tags
    current_tags = set(item.tags.values_list('id', flat=True))

    #candidate items
    candidates = MenuItem.objects.filter(is_available=True).exclude(id=item.id).select_related(
        'category', 'subcategory'
    ).prefetch_related('tags')

    #build a favorites profile instead of looping repeatedly
    favorite_category_ids = set()
    favorite_subcategory_ids = set()
    favorite_tag_ids = set()

    if request.user.is_authenticated:
        favorite_items = request.user.favorites.all().prefetch_related('tags')

        for favorite in favorite_items:
            favorite_category_ids.add(favorite.category_id)
            favorite_subcategory_ids.add(favorite.subcategory_id)
            favorite_tag_ids.update(favorite.tags.values_list('id', flat=True))

    scored_items = []

    for candidate in candidates:
        score = 0
        candidate_tags = set(candidate.tags.values_list('id', flat=True))

        #STRONG similarity to current item
        if candidate.subcategory_id == item.subcategory_id:
            score += 6

        if candidate.category_id == item.category_id:
            score += 3

        shared_tags = current_tags.intersection(candidate_tags)
        score += len(shared_tags) * 2

        #optional price similarity
        if abs(candidate.price - item.price) <= 1:
            score += 1

        #LIGHT personalization from favorites
        if candidate.subcategory_id in favorite_subcategory_ids:
            score += 1

        if candidate.category_id in favorite_category_ids:
            score += 1

        shared_favorite_tags = candidate_tags.intersection(favorite_tag_ids)
        score += len(shared_favorite_tags)

        scored_items.append((score, candidate))

    #sort and take top 3
    scored_items.sort(key=lambda x: x[0], reverse=True)
    recommended_items = [candidate for score, candidate in scored_items[:3]]

    context = {
        'item': item,
        'user_rating': user_rating,
        'average_rating': average_rating,
        'rating_count': rating_count,
        'is_favorited': is_favorited,
        'recommended_items': recommended_items,
    }

    return render(request, 'catalog/item_detail.html', context)

#rating system process/verification
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

#favorite system process/verification
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

#for editing catalog items (admin only)
@staff_member_required
def manage_items(request):
    items = MenuItem.objects.select_related(
        'category',
        'subcategory'
    ).prefetch_related('tags').all()

    return render(request, 'catalog/admin/manage_items.html', {
        'items': items
    })

@staff_member_required
def add_item(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('catalog:manage_items')
    else:
        form = MenuItemForm()

    return render(request, 'catalog/admin/item_form.html', {
        'form': form,
        'title': 'Add Menu Item',
        'button_text': 'Add Item',
    })


@staff_member_required
def edit_item(request, slug):
    item = get_object_or_404(MenuItem, slug=slug)

    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=item)

        if form.is_valid():
            form.save()
            return redirect('catalog:manage_items')
    else:
        form = MenuItemForm(instance=item)

    return render(request, 'catalog/admin/item_form.html', {
        'form': form,
        'title': 'Edit Menu Item',
        'button_text': 'Save Changes',
        'item': item,
    })


@staff_member_required
def delete_item(request, slug):
    item = get_object_or_404(MenuItem, slug=slug)

    if request.method == 'POST':
        item.delete()
        return redirect('catalog:manage_items')

    return render(request, 'catalog/admin/delete_item.html', {
        'item': item,
    })

#for editing categories/subcategories/tags (admin only)
@staff_member_required
def manage_categories(request):
    categories = Category.objects.all()
    subcategories = SubCategory.objects.select_related('category').all()

    return render(request, 'catalog/admin/manage_categories.html', {
        'categories': categories,
        'subcategories': subcategories,
    })


@staff_member_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('catalog:manage_categories')
    else:
        form = CategoryForm()

    return render(request, 'catalog/admin/category_form.html', {
        'form': form,
        'title': 'Add Category',
        'button_text': 'Add Category',
    })


@staff_member_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)

        if form.is_valid():
            form.save()
            return redirect('catalog:manage_categories')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'catalog/admin/category_form.html', {
        'form': form,
        'title': 'Edit Category',
        'button_text': 'Save Changes',
    })


@staff_member_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        category.delete()
        return redirect('catalog:manage_categories')

    return render(request, 'catalog/admin/delete_category.html', {
        'category': category,
    })


@staff_member_required
def add_subcategory(request):
    if request.method == 'POST':
        form = SubCategoryForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('catalog:manage_categories')
    else:
        form = SubCategoryForm()

    return render(request, 'catalog/admin/subcategory_form.html', {
        'form': form,
        'title': 'Add Subcategory',
        'button_text': 'Add Subcategory',
    })


@staff_member_required
def edit_subcategory(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)

    if request.method == 'POST':
        form = SubCategoryForm(request.POST, instance=subcategory)

        if form.is_valid():
            form.save()
            return redirect('catalog:manage_categories')
    else:
        form = SubCategoryForm(instance=subcategory)

    return render(request, 'catalog/admin/subcategory_form.html', {
        'form': form,
        'title': 'Edit Subcategory',
        'button_text': 'Save Changes',
    })


@staff_member_required
def delete_subcategory(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)

    if request.method == 'POST':
        subcategory.delete()
        return redirect('catalog:manage_categories')

    return render(request, 'catalog/admin/delete_subcategory.html', {
        'subcategory': subcategory,
    })