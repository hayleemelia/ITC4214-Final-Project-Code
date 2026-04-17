from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include

def temp_home(request):
    return HttpResponse("Home page placeholder")
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path("", include("core.urls")),
]
