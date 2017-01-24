from django.conf.urls import url
from . import views

app_name = 'userpage'

urlpatterns = [
    url(r'^$', views.get_tmp_homepage, name='tmp_homepage'),
    url(r'^(?P<username>\w+)/$', views.FrontPageView.as_view(), name='front_page'),
    url(r'^(?P<username>\w+)/playlists/(?P<order_type>\w+)/$',
        views.FrontPagePlaylistView.as_view(), name='front_page_playlist'),
    url(r'^(?P<username>\w+)/about/followings/$',
        views.FrontPageAboutFollowingsView.as_view(), name='front_page_about_followings'),
    url(r'^(?P<username>\w+)/about/followers/$',
        views.FrontPageAboutFollowersView.as_view(), name='front_page_about_followers'),
]
