from django.db import models
from django.contrib.auth.models import User


class FrontPageContent(models.Model):
    user = models.OneToOneField(User, related_name='frontpagecontent')
    head_portrait = models.ImageField(upload_to='images/head_portrait/%Y/%m/%d')
    # focus_song = ....

    def __str__(self):
        return 'FrontPageContent of User:{}'.format(self.user.username)

    def save(self, *args, **kwargs):
        # if user have head_portrait, delete the old one
        try:
            this = FrontPageContent.objects.get(id=self.id)
            if this.head_portrait and this.head_portrait != self.head_portrait:
                this.head_portrait.delete(save=False)
        # if new user, do nothing
        except FrontPageContent.DoesNotExist:
            pass
        super(FrontPageContent, self).save()
