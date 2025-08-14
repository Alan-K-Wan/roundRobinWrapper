from django.contrib import admin

from .models import Player

class PlayerAdmin(admin.ModelAdmin):
    list_display = ["peg_name", "peg_colour", "gender"]

admin.site.register(Player, PlayerAdmin)
