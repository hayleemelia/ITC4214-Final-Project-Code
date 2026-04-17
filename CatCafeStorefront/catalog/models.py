from django.db import models
from django.urls import reverse



class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=50)
    slug = models.SlugField()

    class Meta:
        ordering = ['name']
        unique_together = ('category', 'slug')
        verbose_name = "Subcategory"
        verbose_name_plural = "Subcategories"

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='items')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.PROTECT, related_name='items')

    short_description = models.CharField(max_length=200)
    image = models.ImageField(upload_to='menu_items/')
    price = models.DecimalField(max_digits=6, decimal_places=2)

    tags = models.ManyToManyField(Tag, blank=True, related_name='menu_items')

    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category__name', 'subcategory__name', 'name']
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:item_detail', kwargs={'slug': self.slug})
