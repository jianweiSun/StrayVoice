from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    realname = models.CharField(max_length=20, verbose_name='真實姓名', blank=True)
    nickname = models.CharField(max_length=20, verbose_name='暱稱/顯示名稱')
    followings = models.ManyToManyField('self', through='FollowShip',
                                        related_name='followers', symmetrical=False)

    def __str__(self):
        return 'Profile of User:{}'.format(self.user.username)


class FollowShip(models.Model):
    user_from = models.ForeignKey(Profile, related_name='rel_from_set')
    user_to = models.ForeignKey(Profile, related_name='rel_to_set')
    created = models.DateField(auto_now_add=True, db_index=True)

    def __str__(self):
        return "{} follows {}".format(self.user_from, self.user_to)

    class Meta:
        unique_together = ('user_from', 'user_to')
