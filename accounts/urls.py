from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    url(r'^login/$', views.user_login, name='login'),
    url(r'^register/$', views.RegistrationView.as_view(), name='register'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^profile/$', views.ProfileEditView.as_view(), name='profile_edit'),
    url(r'^change_email/$', views.EmailEditView.as_view(), name='email_edit'),
    url(r'^change_password/$', views.PasswordEditView.as_view(), name='password_edit'),
    url(r'^delete_account/$', views.AccountDeleteView.as_view(), name='account_delete'),
    url(r'^follow/$', views.UserFollowView.as_view(), name='user_follow'),
    url(r'^notifications/$', views.NotificationsView.as_view(), name='notifications'),
]
