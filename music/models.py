from django.db import models
from django.contrib.auth.models import User
from .fields import OrderField
from django.urls import reverse


class Album(models.Model):
    user = models.ForeignKey(User, related_name='albums')
    name = models.CharField(max_length=30)
    description = models.TextField(max_length=500, blank=True)
    cover = models.ImageField(upload_to='images/album_cover/%Y/%m/%d', blank=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    liked_by = models.ManyToManyField(User, through='AlbumLikeShip', related_name='like_albums')
    total_likes = models.IntegerField(default=0)

    class Meta:
        ordering = ('-created', )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('music:album_detail', args=[self.user.username, self.id])

    def save(self, *args, **kwargs):
        # if album have cover, delete the old one
        try:
            this = Album.objects.get(id=self.id)
            if this.cover and this.cover != self.cover:
                this.cover.delete(save=False)
        # if new album, do nothing
        except Album.DoesNotExist:
            pass
        super(Album, self).save()


class Song(models.Model):
    GENRE_CHOICES = [(0, '未分類曲風'),
                     (1, 'Hip hop/ Rap'),
                     (2, 'Rock'),
                     (3, 'R&B/ Soul'),
                     (4, 'Singer/ Songwriter')]
    AUTHORIZATION_CHOICES = [(0, '版權所有'),
                             (1, '姓名標示'),
                             (2, '姓名標示-非商業性')]
    PUBLISHED_CHOICES = [(True, '公開'),
                         (False, '隱藏')]
    user = models.ForeignKey(User, related_name='songs')
    album = models.ForeignKey(Album, related_name='songs')
    order = OrderField(blank=True, for_fields=['album'], db_index=True)
    file = models.FileField(upload_to='songs/%Y/%m/%d/')
    length = models.CharField(max_length=8)
    cover = models.ImageField(upload_to='images/song_cover/%Y/%m/%d', blank=True)
    name = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    genre = models.IntegerField(choices=GENRE_CHOICES, default=0)
    authorization = models.IntegerField(choices=AUTHORIZATION_CHOICES, default=0)
    published = models.BooleanField(choices=PUBLISHED_CHOICES, default=True)
    lyrics = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    liked_by = models.ManyToManyField(User, through='SongLikeShip', related_name='like_songs')
    total_likes = models.IntegerField(default=0)

    class Meta:
        ordering = ('-created', 'user')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('music:song_detail', args=[self.user.username, self.id])

    def save(self, *args, **kwargs):
        # if song have cover or file, delete the old one
        try:
            this = Song.objects.get(id=self.id)
            album = this.album
            # avoid delete album cover if songs use it
            if this.cover and this.cover != album.cover and this.cover != self.cover:
                this.cover.delete(save=False)
            if this.file and this.file != self.file:
                this.file.delete(save=False)
        # if new song, do nothing
        except Song.DoesNotExist:
            pass
        super(Song, self).save()


class SongLikeShip(models.Model):
    user = models.ForeignKey(User)
    song = models.ForeignKey(Song)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return '{} likes {}'.format(self.user, self.song)

    class Meta:
        unique_together = ("user", "song")


class AlbumLikeShip(models.Model):
    user = models.ForeignKey(User)
    album = models.ForeignKey(Album)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return '{} likes {}'.format(self.user, self.album)

    class Meta:
        unique_together = ("user", "album")


class Playlist(models.Model):
    PUBLISHED_CHOICES = [(True, '公開'),
                         (False, '隱藏')]
    user = models.ForeignKey(User, related_name='playlists')
    name = models.CharField(max_length=30)
    description = models.TextField(max_length=500, blank=True)
    cover = models.ImageField(upload_to='images/playlist_cover/%Y/%m/%d', blank=True)
    published = models.BooleanField(choices=PUBLISHED_CHOICES, default=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    songs = models.ManyToManyField(Song, through='PlaylistSongsShip', related_name='playlists')
    liked_by = models.ManyToManyField(User, through='PlaylistLikeShip', related_name='like_playlists')
    total_likes = models.IntegerField(default=0)

    class Meta:
        ordering = ('-created', )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('music:playlist_detail', args=[self.user.username, self.id])

    def save(self, *args, **kwargs):
        # if playlist have cover, delete the old one
        try:
            this = Playlist.objects.get(id=self.id)
            if this.cover and this.cover != self.cover:
                this.cover.delete(save=False)
        # if new playlist, do nothing
        except Playlist.DoesNotExist:
            pass
        super(Playlist, self).save()


class PlaylistLikeShip(models.Model):
    user = models.ForeignKey(User)
    playlist = models.ForeignKey(Playlist)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return '{} likes {}'.format(self.user, self.playlist)

    class Meta:
        unique_together = ("user", "playlist")


class PlayListSongsShip(models.Model):
    playlist = models.ForeignKey(Playlist)
    song = models.ForeignKey(Song)
    order = OrderField(blank=True, for_fields=['playlist'], db_index=True)

    def __str__(self):
        return '{} contains {}'.format(self.playlist, self.song)

