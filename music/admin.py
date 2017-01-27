from django.contrib import admin
from .models import Album, Song, Playlist, AlbumLikeShip, SongLikeShip, PlaylistLikeShip, PlayListSongsShip


class AlbumAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Album._meta.fields]


class AlbumLikeShipAdmin(admin.ModelAdmin):
    list_display = [f.name for f in AlbumLikeShip._meta.fields]


class SongAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Song._meta.fields]


class SongLikeShipAdmin(admin.ModelAdmin):
    list_display = [f.name for f in SongLikeShip._meta.fields]


class PlaylistAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Playlist._meta.fields]


class PlaylistLikeShipAdmin(admin.ModelAdmin):
    list_display = [f.name for f in PlaylistLikeShip._meta.fields]


class PlayListSongsShipAdmin(admin.ModelAdmin):
    list_display = [f.name for f in PlayListSongsShip._meta.fields]


admin.site.register(Album, AlbumAdmin)
admin.site.register(AlbumLikeShip, AlbumLikeShipAdmin)
admin.site.register(Song, SongAdmin)
admin.site.register(SongLikeShip, SongLikeShipAdmin)
admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(PlaylistLikeShip, PlaylistLikeShipAdmin)
admin.site.register(PlayListSongsShip, PlayListSongsShipAdmin)
