from django.conf import settings
from django.db import models
from catalog.models import MenuItem


class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='ratings')
    value = models.PositiveSmallIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'item')

    def __str__(self):
        return f"{self.user.username} rated {self.item.name}: {self.value}"