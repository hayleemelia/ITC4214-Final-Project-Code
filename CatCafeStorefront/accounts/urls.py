from django.urls import path
from .views import register_view, CustomLoginView, CustomLogoutView, profile_view, manage_users, edit_user

app_name = "accounts"
urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', profile_view, name='profile'),
    path('admin/users/', manage_users, name='manage_users'),
    path('admin/users/<int:pk>/edit/', edit_user, name='edit_user'),
]
