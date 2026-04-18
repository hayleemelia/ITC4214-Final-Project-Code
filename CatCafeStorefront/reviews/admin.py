from django.contrib import admin
from .models import Rating


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'score', 'updated_at')
    list_filter = ('score', 'updated_at')
    search_fields = ('user__username', 'item__name')