from django.conf.urls import url
from . import views
import re
app_name = 'browse'
urlpatterns = [
    # songs
    url(r'^songs/general/(?P<genre>\w+)/(?P<order_type>\w+)/$', views.BrowseAllView.as_view(), name='browse_all'),
    url(r'^songs/likes/(?P<genre>\w+)/(?P<order_type>\w+)/$', views.BrowseLikeView.as_view(), name='browse_like'),
    url(r'^songs/follows/(?P<genre>\w+)/(?P<order_type>\w+)/$', views.BrowseFollowView.as_view(), name='browse_follow'),
    # playlists
    url(r'^playlists/general/(?P<order_type>\w+)/$'
        , views.PlaylistBrowseAllView.as_view(), name='playlist_browse_all'),
    url(r'^playlists/mine/(?P<order_type>\w+)/$'
        , views.PlaylistBrowseMineView.as_view(), name='playlist_browse_mine'),
    url(r'^playlists/like/(?P<order_type>\w+)/$'
        , views.PlaylistBrowseLikeView.as_view(), name='playlist_browse_like'),
]
