from django.conf.urls import url
from . import views
import re
app_name = 'browse'
urlpatterns = [
    url(r'^general/(?P<genre>\w+)/(?P<order_type>\w+)/$', views.BrowseAllView.as_view(), name='browse_all'),
    url(r'^likes/(?P<genre>\w+)/(?P<order_type>\w+)/$', views.BrowseLikeView.as_view(), name='browse_like'),
]
