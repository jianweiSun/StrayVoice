from django.conf.urls import url
from . import views

app_name = 'userpage'

urlpatterns = [
    url(r'^$', views.get_tmp_homepage, name='tmp_homepage'),
    url(r'(?P<username>\w+)/$', views.FrontPageView.as_view(), name='front_page'),
]