from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    realname = models.CharField(max_length=20, verbose_name='真實姓名', blank=True)
    nickname = models.CharField(max_length=20, verbose_name='暱稱/顯示名稱')

    def __str__(self):
        return 'Profile of User:{}'.format(self.user.username)

