from django.conf.urls import url
from . import views

app_name = 'music'
urlpatterns = [
    url(r'^manage/song/upload/$', views.SongCreateView.as_view(), name='song_create'),
    url(r'^manage/song/(?P<song_id>\d+)/$', views.SongEditView.as_view(), name='song_edit'),
    url(r'^manage/song/(?P<song_id>\d+)/delete/$', views.SongDeleteView.as_view(), name='song_delete'),
    url(r'^manage/song/(?P<song_id>\d+)/change_album/$',
        views.SongChangeAlbumView.as_view(), name='song_change_album'),
    url(r'^manage/album/create/$', views.AlbumCreateView.as_view(), name='album_create'),
    url(r'^manage/album/song_order/$', views.AlbumSongsOrderView.as_view(), name='album_songs_order'),
    url(r'^manage/album/(?P<album_id>\d+)/$', views.AlbumEditView.as_view(), name='album_edit'),
    url(r'^manage/album/(?P<album_id>\d+)/delete/$', views.AlbumDeleteView.as_view(), name='album_delete'),
    url(r'^manage/album/apply_covers/$',
        views.AlbumCoverApplySongsView.as_view(), name="album_apply_covers"),
    url(r'^manage/unalbum/songs/$', views.UnAlbumSongsEditView.as_view(), name='un_album_songs'),
    url(r'^(?P<username>\w+)/songs/(?P<song_id>\d+)/',
        views.SongDetailView.as_view(), name='song_detail'),
    url(r'^(?P<username>\w+)/album/(?P<album_id>\d+)/',
        views.AlbumDetailView.as_view(), name='album_detail'),
    url(r'^song_like/$', views.SongLikeView.as_view(), name='song_like'),
]
