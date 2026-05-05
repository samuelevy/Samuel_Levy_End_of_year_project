from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Player

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'get_name', 'elo', 'glicko', 'tries', 'last_game_date')
    list_filter = ('last_game_date',)
    search_fields = ('user__name',)
    
    def get_name(self, obj):
        return obj.user.name
    get_name.short_description = 'Name'