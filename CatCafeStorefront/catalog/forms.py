from django import forms
from .models import MenuItem, Category, SubCategory, Tag


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = [
            'name',
            'slug',
            'category',
            'subcategory',
            'short_description',
            'image',
            'price',
            'tags',
            'is_available',
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'subcategory': forms.Select(attrs={'class': 'form-select'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        }


class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['category', 'name', 'slug']

        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'slug']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        }