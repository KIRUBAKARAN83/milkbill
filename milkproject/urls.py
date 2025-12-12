from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Root homepage → accounts home view
    path('', include('accounts.urls')),  

    # Keep accounts/ if you want a second access path
    # path('accounts/', include('accounts.urls')), 
]
