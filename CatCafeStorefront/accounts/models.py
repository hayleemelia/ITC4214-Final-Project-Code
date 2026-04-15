from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    #favorites = models.ManyToManyField('catalog.Item', blank=True)

    def __str__(self):
        return self.username
