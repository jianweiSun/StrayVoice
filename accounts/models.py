from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    realname = models.CharField(max_length=20, verbose_name='真實姓名', blank=True)
    nickname = models.CharField(max_length=20, verbose_name='暱稱/顯示名稱')
    followings = models.ManyToManyField('self', through='FollowShip',
                                        related_name='followers', symmetrical=False,
                                        through_fields=('profile_from', 'profile_to'))
    total_followers = models.IntegerField(default=0)

    def __str__(self):
        return 'Profile of User:{}'.format(self.user.username)


class FollowShip(models.Model):
    profile_from = models.ForeignKey(Profile, related_name='follow_from_set')
    profile_to = models.ForeignKey(Profile, related_name='follow_to_set')
    created = models.DateField(auto_now_add=True, db_index=True)

    def __str__(self):
        return "{} follows {}".format(self.profile_from, self.profile_to)

    class Meta:
        unique_together = ('profile_from', 'profile_to')
