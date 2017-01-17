from django.contrib import admin
from .models import Album, Song


class AlbumAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'description', 'cover')


class SongAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Song._meta.fields]

admin.site.register(Album, AlbumAdmin)
admin.site.register(Song, SongAdmin)
