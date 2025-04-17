from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Game

# Register the Game model
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('player', 'player_choice', 'computer_choice', 'result', 'created_at')
    list_filter = ('result', 'created_at')
    search_fields = ('player__username',)
    date_hierarchy = 'created_at'

# Re-register UserAdmin
admin.site.unregister(User)
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
