from django.contrib import admin
from .models import Profile, FollowShip


class ProfileAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Profile._meta.fields]


class FollowShipAdmin(admin.ModelAdmin):
    list_display = [f.name for f in FollowShip._meta.fields]


admin.site.register(Profile, ProfileAdmin)
admin.site.register(FollowShip, FollowShipAdmin)
