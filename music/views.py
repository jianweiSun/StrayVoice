from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import SongCreateForm, AlbumCreateForm, SongChangeAlbumForm, PlaylistCreateForm, PlaylistAddSongsForm
from django.contrib import messages
from .models import Album, Song, SongLikeShip, AlbumLikeShip, Playlist, PlayListSongsShip
from django.urls import reverse
from django.http import HttpResponseNotFound, HttpResponseForbidden, JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from playqueue.decorators import ajax_required
from django.db.models import F
import json


class SongCreateView(TemplateResponseMixin, LoginRequiredMixin, View):
    template_name = 'music/manage/song_create.html'

    def get(self, request):
        # take user in to produce dynamic ModelChoiceField of album
        form = SongCreateForm(user=request.user)
        return self.render_to_response({'form': form})

    def post(self, request):
        form = SongCreateForm(user=request.user,
                              data=request.POST,
                              files=request.FILES)
        if form.is_valid():
            album = form.cleaned_data['album']
            song = form.save(commit=False)
            song.user = request.user
            song.album = album
            song.save()
            return redirect(reverse('music:song_edit', args=[song.id]))
        else:
            return self.render_to_response({'form': form})


class SongEditView(TemplateResponseMixin, LoginRequiredMixin, View):
    template_name = 'music/manage/song_edit.html'

    def dispatch(self, request, *args, song_id=None, **kwargs):
        self.song = get_object_or_404(Song, user=request.user, id=song_id)
        return super(SongEditView, self).dispatch(request, *args, song_id, **kwargs)

    def get(self, request, song_id):
        form = SongCreateForm(user=request.user,
                              instance=self.song,
                              initial={'album': self.song.album})
        return self.render_to_response({'form': form,
                                        'song': self.song,
                                        'section': 'music_management'})

    def post(self, request, song_id):
        form = SongCreateForm(user=request.user,
                              data=request.POST,
                              files=request.FILES,
                              instance=self.song)
        if form.is_valid():
            prev_album = self.song.album
            album = form.cleaned_data['album']
            song = form.save(commit=False)
            # if change album, reset order to trigger auto-set of orderfield
            if prev_album != album:
                song.order = None
            song.album = album
            song.save()
            messages.success(request, '歌曲編輯成功')
            # update the form, so that we can update the input immediately
            form = SongCreateForm(user=request.user,
                                  instance=song,
                                  initial={'album': song.album})
        else:
            messages.error(request, '歌曲編輯失敗')
        return self.render_to_response({'form': form,
                                        'song': self.song,
                                        'section': 'music_management'})


class SongDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'music/manage/song_delete.html'

    def dispatch(self, request, *args, song_id=None, **kwargs):
        self.song = get_object_or_404(Song, user=request.user, id=song_id)
        self.album = self.song.album
        self.all_albums = Album.objects.filter(user=request.user) \
                                       .exclude(name__contains="未分類專輯")
        return super(SongDeleteView, self).dispatch(request, *args, song_id, **kwargs)

    def get_object(self, queryset=None):
        return self.song

    def get_context_data(self, **kwargs):
        context = super(SongDeleteView, self).get_context_data(**kwargs)
        context['song'] = self.song
        context['album'] = self.album
        context['all_albums'] = self.all_albums
        return context

    def get_success_url(self):
        return reverse('music:album_edit', args=[self.album.id])


class SongDetailView(TemplateResponseMixin, View):
    template_name = 'music/song_detail.html'

    def get(self, request, username, song_id):
        owner = get_object_or_404(User, username=username)
        song = get_object_or_404(Song, user=owner, id=song_id)
        return self.render_to_response({'song': song})


class AlbumCreateView(TemplateResponseMixin, LoginRequiredMixin, View):
    template_name = 'music/manage/album_create.html'

    def get(self, request):
        form = AlbumCreateForm()
        all_albums = Album.objects.filter(user=request.user)\
                                  .exclude(name__contains="未分類專輯")
        return self.render_to_response({'form': form,
                                        'section': 'music_management',
                                        'all_albums': all_albums})

    def post(self, request):
        form = AlbumCreateForm(data=request.POST,
                               files=request.FILES)
        if form.is_valid():
            album = form.save(commit=False)
            album.user = request.user
            album.save()
            messages.success(request, '專輯新增成功')
            return redirect(reverse('music:album_edit', args=[album.id]))
        else:
            messages.error(request, '專輯新增失敗')
        return self.render_to_response({'form': form,
                                        'section': 'music_management'})


class AlbumEditView(TemplateResponseMixin, LoginRequiredMixin, View):
    template_name = 'music/manage/album_edit.html'

    def dispatch(self, request, *args, album_id=None, **kwargs):
        self.album = get_object_or_404(Album, user=request.user, id=album_id)

        # redirect if user try to modify default
        if self.album.name == '未分類專輯':
            return redirect(reverse('music:un_album_songs'))

        self.songs = Song.objects.filter(album=self.album).order_by('order')
        return super(AlbumEditView, self).dispatch(request, *args, album_id, **kwargs)

    def get(self, request, album_id):
        form = AlbumCreateForm(instance=self.album)
        all_albums = Album.objects.filter(user=request.user) \
                                  .exclude(name__contains="未分類專輯")
        return self.render_to_response({'form': form,
                                        'album': self.album,
                                        'songs': self.songs,
                                        'section': 'music_management',
                                        'all_albums': all_albums})

    def post(self, request, album_id):
        form = AlbumCreateForm(data=request.POST,
                               files=request.FILES,
                               instance=self.album)
        all_albums = Album.objects.filter(user=request.user) \
                                  .exclude(name__contains="未分類專輯")
        if form.is_valid():
            form.save()
            messages.success(request, '專輯編輯成功')
        else:
            messages.success(request, '專輯編輯失敗')
        return self.render_to_response({'form': form,
                                        'album': self.album,
                                        'songs': self.songs,
                                        'section': 'music_management',
                                        'all_albums': all_albums})


class AlbumDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'music/manage/album_delete.html'

    def dispatch(self, request, *args, album_id=None, **kwargs):
        self.album = get_object_or_404(Album, user=request.user, id=album_id)
        self.all_albums = Album.objects.filter(user=request.user) \
                                       .exclude(name__contains="未分類專輯")
        # disallow user to delete default album
        if self.album.name == "未分類專輯":
            return HttpResponseNotFound()

        return super(AlbumDeleteView, self).dispatch(request, *args, album_id, **kwargs)

    def get_object(self, queryset=None):
        return self.album

    def get_context_data(self, **kwargs):
        context = super(AlbumDeleteView, self).get_context_data(**kwargs)
        context['album'] = self.album
        context['all_albums'] = self.all_albums
        return context

    def get_success_url(self):
        return reverse('music:un_album_songs')

    def delete(self, request, *args, **kwargs):
        default = get_object_or_404(Album, user=request.user, name="未分類專輯")
        all_songs = self.album.songs.order_by('order')
        for song in all_songs:
            # set None to auto-set the order, maybe there're better ways
            song.album = default
            song.order = None
            song.save()
        return super(AlbumDeleteView, self).delete(request, *args, **kwargs)


class AlbumDetailView(TemplateResponseMixin, View):
    template_name = 'music/album_detail.html'

    def get(self, request, username, album_id):
        owner = get_object_or_404(User, username=username)
        album = get_object_or_404(Album, user=owner, id=album_id)
        songs = album.songs.order_by('order')
        # don't show default album
        if album.name == '未分類專輯':
            return HttpResponseNotFound()
        return self.render_to_response({'album': album,
                                        'songs': songs})


class UnAlbumSongsEditView(TemplateResponseMixin, LoginRequiredMixin, View):
    template_name = 'music/manage/un_album_songs.html'

    def get(self, request):
        album = get_object_or_404(Album, user=request.user, name='未分類專輯')
        songs = album.songs.order_by('order')
        all_albums = Album.objects.filter(user=request.user) \
                                  .exclude(name__contains="未分類專輯")
        return self.render_to_response({'songs': songs,
                                        'all_albums': all_albums,
                                        'album': album,
                                        'section': 'music_management'})


class SongChangeAlbumView(TemplateResponseMixin, LoginRequiredMixin, View):
    template_name = 'music/manage/song_change_album.html'

    def dispatch(self, request, *args, song_id=None, **kwargs):
        self.song = get_object_or_404(Song, user=request.user, id=song_id)
        return super(SongChangeAlbumView, self).dispatch(request, *args, song_id, **kwargs)

    def get(self, request, song_id):
        form = SongChangeAlbumForm(user=request.user,
                                   initial={'album': self.song.album})
        return self.render_to_response({'form': form,
                                        'song': self.song})

    def post(self, request, song_id):
        form = SongChangeAlbumForm(user=request.user,
                                   data=request.POST)
        if form.is_valid():
            prev_album = self.song.album
            album = form.cleaned_data['album']
            # if change album, reset order to None, let OrderField handle it automatically
            # also , if album is not changed, do nothing
            if prev_album != album:
                self.song.order = None
                self.song.album = album
                self.song.save()
            return redirect(reverse('music:album_edit', args=[prev_album.id]))
        else:
            return HttpResponseForbidden()


@method_decorator(ajax_required, name='dispatch')
class AlbumCoverApplySongsView(LoginRequiredMixin, View):

    def post(self, request):
        album_id = request.POST.get('album_id')
        album = get_object_or_404(Album, user=request.user, id=album_id)
        album_cover = album.cover
        album.songs.update(cover=album_cover)
        return redirect(reverse('music:album_edit', args=[album_id]))


@method_decorator(ajax_required, name='dispatch')
class AlbumSongsOrderView(LoginRequiredMixin, View):

    def post(self, request):
        for song_id, new_order in json.loads(request.body.decode()).items():
            # maybe there're other ways to update it without hit database several times
            # by raw SQL...
            Song.objects.filter(user=request.user, id=song_id).update(order=new_order)
        return JsonResponse({'saved': 'OK'})


@method_decorator(ajax_required, name='dispatch')
class SongLikeView(LoginRequiredMixin, View):

    def post(self, request):
        song_id = request.POST.get('song_id')
        action = request.POST.get('action')

        song = get_object_or_404(Song, id=song_id)
        if action == 'like':
            SongLikeShip.objects.create(user=request.user, song=song)
            song.total_likes = song.liked_by.count()
            song.save()
        else:
            SongLikeShip.objects.filter(user=request.user, song=song).delete()
            song.total_likes = song.liked_by.count()
            song.save()
        return JsonResponse({'saved': 'OK'})


@method_decorator(ajax_required, name='dispatch')
class AlbumLikeView(LoginRequiredMixin, View):

    def post(self, request):
        album_id = request.POST.get('album_id')
        action = request.POST.get('action')

        album = get_object_or_404(Album, id=album_id)
        if album.name == '未分類專輯':
            return HttpResponseNotFound()

        if action == 'like':
            AlbumLikeShip.objects.create(user=request.user, album=album)
            album.total_likes = album.liked_by.count()
            album.save()
        else:
            AlbumLikeShip.objects.filter(user=request.user, album=album).delete()
            album.total_likes = album.liked_by.count()
            album.save()
        return JsonResponse({'saved': 'OK'})


class PlaylistCreateView(TemplateResponseMixin, LoginRequiredMixin, View):
    template_name = 'music/manage/playlist_create.html'

    def get(self, request):
        form = PlaylistCreateForm()
        all_playlists = Playlist.objects.filter(user=request.user)

        return self.render_to_response({'form': form,
                                        'section': 'playlist_management',
                                        'all_playlists': all_playlists})

    def post(self, request):
        form = PlaylistCreateForm(data=request.POST,
                                  files=request.FILES)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.user = request.user
            playlist.save()
            messages.success(request, '歌單新增成功')
            return redirect(reverse('music:playlist_edit', args=[playlist.id]))
        else:
            messages.error(request, '歌單新增失敗')
        return self.render_to_response({'form': form,
                                        'section': 'playlist_management'})


class PlaylistEditView(TemplateResponseMixin, LoginRequiredMixin, View):
    template_name = 'music/manage/playlist_edit.html'

    def dispatch(self, request, *args, playlist_id=None, **kwargs):
        self.playlist = get_object_or_404(Playlist, user=request.user, id=playlist_id)
        self.songs = self.playlist.songs\
                                  .order_by('playlistsongsship__order')\
                                  .annotate(playlistsongsship_id=F('playlistsongsship__id'))
        return super(PlaylistEditView, self).dispatch(request, *args, playlist_id, **kwargs)

    def get(self, request, playlist_id):
        form = PlaylistCreateForm(instance=self.playlist)
        all_playlists = Playlist.objects.filter(user=request.user)

        return self.render_to_response({'form': form,
                                        'playlist': self.playlist,
                                        'songs': self.songs,
                                        'section': 'playlist_management',
                                        'all_playlists': all_playlists})

    def post(self, request, playlist_id):
        form = PlaylistCreateForm(data=request.POST,
                                  files=request.FILES,
                                  instance=self.playlist)
        all_playlists = Playlist.objects.filter(user=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, '歌單編輯成功')
        else:
            messages.success(request, '歌單編輯失敗')
        return self.render_to_response({'form': form,
                                        'playlist': self.playlist,
                                        'songs': self.songs,
                                        'section': 'playlist_management',
                                        'all_playlists': all_playlists})


class PlaylistDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'music/manage/playlist_delete.html'

    def dispatch(self, request, *args, playlist_id=None, **kwargs):
        self.user = request.user
        self.playlist = get_object_or_404(Playlist, user=request.user, id=playlist_id)
        self.all_playlists = Playlist.objects.filter(user=request.user)

        return super(PlaylistDeleteView, self).dispatch(request, *args, playlist_id, **kwargs)

    def get_object(self, queryset=None):
        return self.playlist

    def get_context_data(self, **kwargs):
        context = super(PlaylistDeleteView, self).get_context_data(**kwargs)
        context['playlist'] = self.playlist
        context['all_playlists'] = self.all_playlists
        return context

    def get_success_url(self):
        return reverse('music:playlist_create')


class PlaylistDetailView(TemplateResponseMixin, View):
    template_name = 'music/playlist_detail.html'

    def get(self, request, username, playlist_id):
        owner = get_object_or_404(User, username=username)
        playlist = get_object_or_404(Playlist, user=owner, id=playlist_id)
        songs = playlist.songs.order_by('playlistsongsship__order')

        return self.render_to_response({'playlist': playlist,
                                        'songs': songs})


@method_decorator(ajax_required, name='dispatch')
class PlaylistAddSongsView(TemplateResponseMixin, LoginRequiredMixin, View):
    template_name = 'music/manage/playlist_add_songs.html'

    def dispatch(self, request, *args, model_type=None, id=None, **kwargs):
        type_choice = {'song', 'album', 'playlist'}
        if model_type not in type_choice:
            return HttpResponseNotFound()

        if model_type == 'song':
            self.song = get_object_or_404(Song, id=id)
        elif model_type == 'album':
            self.album = get_object_or_404(Album, id=id)
        else:
            self.playlist = get_object_or_404(Playlist, id=id)
        return super(PlaylistAddSongsView, self).dispatch(request, *args, model_type, id, **kwargs)

    def get(self, request, model_type, id):
        if not request.user.playlists.all():
            template_name = 'music/manage/playlist_not_exist.html'
            return self.render_to_response({})

        form = PlaylistAddSongsForm(user=request.user)
        return self.render_to_response({'form': form})

    def post(self, request, model_type, id):
        form = PlaylistAddSongsForm(user=request.user,
                                    data=request.POST)
        if form.is_valid():
            playlist = form.cleaned_data['playlist']
            if model_type == 'song':
                PlayListSongsShip.objects.create(playlist=playlist, song=self.song)
            elif model_type == 'album':
                # maybe can use bulk_create or transaction to improve performance
                for song in self.album.songs.order_by('order'):
                    PlayListSongsShip.objects.create(playlist=playlist, song=song)
            else:
                for song in self.playlist.songs.order_by('playlistsongsship__order'):
                    PlayListSongsShip.objects.create(playlist=playlist, song=song)
            return JsonResponse({'saved': 'OK'})
        else:
            return HttpResponseForbidden()


@method_decorator(ajax_required, name='dispatch')
class PlaylistDeleteSongView(LoginRequiredMixin, View):

    def post(self, request):
        id = request.POST.get('playlistsongsship_id')
        PlayListSongsShip.objects.get(id=id).delete()
        return JsonResponse({'saved': 'OK'})


@method_decorator(ajax_required, name='dispatch')
class SongChangePlaylistView(LoginRequiredMixin, TemplateResponseMixin, View):
    template_name = 'music/manage/playlist_add_songs.html'

    def get(self, request):
        form = PlaylistAddSongsForm(user=request.user)
        return self.render_to_response({'form': form})

    def post(self, request):
        form = PlaylistAddSongsForm(user=request.user,
                                    data=request.POST)
        if form.is_valid():
            new_playlist = form.cleaned_data['playlist']
            playlistship_id = request.POST.get('playlistsongsship_id')
            playlistship_obj = PlayListSongsShip.objects.get(id=playlistship_id)

            if playlistship_obj.playlist == new_playlist:
                return JsonResponse({'saved': 'No'})
            else:
                playlistship_obj.order = None
                playlistship_obj.playlist = new_playlist
                playlistship_obj.save()
                return JsonResponse({'saved': 'OK'})
        else:
            return HttpResponseForbidden()


@method_decorator(ajax_required, name='dispatch')
class PlaylistSongsOrderView(LoginRequiredMixin, View):

    def post(self, request):
        for id, new_order in json.loads(request.body.decode()).items():
            PlayListSongsShip.objects.filter(id=id).update(order=new_order)
        return JsonResponse({'saved': 'OK'})
