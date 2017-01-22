from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from ..forms import PlaylistCreateForm, PlaylistAddSongsForm
from django.contrib import messages
from ..models import Album, Song, Playlist, PlayListSongsShip
from django.urls import reverse
from django.http import HttpResponseNotFound, HttpResponseForbidden, JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from playqueue.decorators import ajax_required
from django.db.models import F
import json


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
