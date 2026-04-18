from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class Rating(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    item = models.ForeignKey(
        'catalog.MenuItem',
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'item')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} rated {self.item.name}: {self.score}/5"