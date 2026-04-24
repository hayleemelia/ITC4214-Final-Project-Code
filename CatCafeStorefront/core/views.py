from django.shortcuts import render
from django.db.models import Avg, Count
from catalog.models import MenuItem


def home(request):
    popular_items = MenuItem.objects.filter(is_available=True).annotate(
        avg_rating=Avg('ratings__score'),
        rating_count=Count('ratings')
    ).filter(
        rating_count__gt=0
    ).order_by(
        '-avg_rating',
        '-rating_count'
    )[:3]

    return render(request, 'core/index.html', {
        'popular_items': popular_items,
    })