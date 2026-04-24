from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, CustomAuthenticationForm, CustomUserChangeForm, AdminUserUpdateForm
from django.urls import reverse_lazy

#creating the registration view
def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('core:home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})

#creating the login view
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True

#creating the logout view
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('core:home')

#profile view
@login_required
def profile_view(request):
    user = request.user

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile')
    else:
        form = CustomUserChangeForm(instance=user)

    favorite_items = user.favorites.all().select_related('category', 'subcategory').prefetch_related('tags')

    context = {
        'form': form,
        'favorite_items': favorite_items,
    }

    return render(request, 'accounts/profile.html', context)

#management views
User = get_user_model()


@staff_member_required
def manage_users(request):
    users = User.objects.all().order_by('username')

    return render(request, 'accounts/admin/manage_users.html', {
        'users': users,
    })


@staff_member_required
def edit_user(request, pk):
    selected_user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = AdminUserUpdateForm(request.POST, instance=selected_user)

        if form.is_valid():
            form.save()
            return redirect('accounts:manage_users')
    else:
        form = AdminUserUpdateForm(instance=selected_user)

    return render(request, 'accounts/admin/user_form.html', {
        'form': form,
        'selected_user': selected_user,
    })
