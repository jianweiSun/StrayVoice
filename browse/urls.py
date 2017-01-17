from django.conf.urls import url
from . import views
import re
app_name = 'browse'
urlpatterns = [
    url(r'^general/(?P<genre>\w+)/(?P<order_type>\w+)/$', views.BrowseAllView.as_view(), name='browse_all'),
]
