from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.menu_list, name='menu_list'),
    path('<slug:slug>/', views.item_detail, name='item_detail'),
    path('menu/<slug:slug>/rate/', views.rate_item, name='rate_item'),
    path('menu/<slug:slug>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('admin/items/', views.manage_items, name='manage_items'),
    path('admin/items/add/', views.add_item, name='add_item'),
    path('admin/items/<slug:slug>/edit/', views.edit_item, name='edit_item'),
    path('admin/items/<slug:slug>/delete/', views.delete_item, name='delete_item'),
    path('admin/categories/', views.manage_categories, name='manage_categories'),

    path('admin/categories/add/', views.add_category, name='add_category'),
    path('admin/categories/<int:pk>/edit/', views.edit_category, name='edit_category'),
    path('admin/categories/<int:pk>/delete/', views.delete_category, name='delete_category'),

    path('admin/subcategories/add/', views.add_subcategory, name='add_subcategory'),
    path('admin/subcategories/<int:pk>/edit/', views.edit_subcategory, name='edit_subcategory'),
    path('admin/subcategories/<int:pk>/delete/', views.delete_subcategory, name='delete_subcategory'),
    path('admin/tags/add/', views.add_tag, name='add_tag'),
    path('admin/tags/<int:pk>/edit/', views.edit_tag, name='edit_tag'),
    path('admin/tags/<int:pk>/delete/', views.delete_tag, name='delete_tag'),
    ]