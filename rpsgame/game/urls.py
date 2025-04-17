from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomUserCreationForm
from django.views.generic import CreateView

urlpatterns = [
    path('', views.home, name='home'),
    path('play/', views.play_game, name='play'),
    path('history/', views.game_history, name='history'),
    # VULNERABILITY: Insecure Design - Debug endpoint exposing admin functionality
    path('debug/become_admin/', views.become_admin, name='become_admin'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/signup/', CreateView.as_view(
        template_name='registration/signup.html',
        form_class=CustomUserCreationForm,
        success_url='/play/'
    ), name='signup'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('high-scores/', views.high_score_table, name='high_score_table'),
]