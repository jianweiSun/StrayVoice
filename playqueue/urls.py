from django.conf.urls import url
from . import views

app_name = 'playqueue'

urlpatterns = [
    url(r'^song/(?P<song_id>\d+)/prepend/$',
        views.PlayQueuePrepend.as_view(), name='song_prepend'),
    url(r'^song/(?P<song_id>\d+)/append/$',
        views.PlayQueueAppend.as_view(), name='song_append'),
    url(r'^(?P<index>\d+)/remove/$', views.PlayQueueRemove.as_view(), name='queue_remove'),
    url(r'^clear/$', views.PlayQueueClear.as_view(), name='queue_clear'),
    url(r'^exchange/$', views.PlayQueueExchange.as_view(), name='queue_exchange'),
    url(r'^exchange/album/(?P<album_id>\d+)/',
        views.AlbumSongsExchange.as_view(), name='album_exchange'),
    url(r'^album/(?P<album_id>\d+)/append/$',
        views.AlbumSongsAppend.as_view(), name='album_append'),
]
