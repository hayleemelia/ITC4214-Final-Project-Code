from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.menu_list, name='menu_list'),
    path('<slug:slug>/', views.item_detail, name='item_detail'),
    path('menu/<slug:slug>/rate/', views.rate_item, name='rate_item'),
]