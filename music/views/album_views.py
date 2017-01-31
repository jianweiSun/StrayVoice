from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from ..forms import AlbumCreateForm, SongChangeAlbumForm
from django.contrib import messages
from ..models import Album, Song, AlbumLikeShip
from django.urls import reverse
from django.http import HttpResponseNotFound, HttpResponseForbidden, JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from playqueue.decorators import ajax_required
import json


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
        all_albums = Album.objects.filter(user=request.user)\
                                  .exclude(name__contains="未分類專輯")

        if form.is_valid():
            album = form.save(commit=False)
            album.user = request.user
            album.save()
            messages.success(request, '專輯新增成功')
            return redirect(reverse('music:album_edit', args=[album.id]))
        else:
            messages.error(request, '專輯新增失敗')
        return self.render_to_response({'form': form,
                                        'section': 'music_management',
                                        'all_albums': all_albums})


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
            messages.error(request, '專輯編輯失敗')
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
        # don't show default album
        if album.name == '未分類專輯':
            return HttpResponseNotFound()
        return self.render_to_response({'album': album})


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


@method_decorator(ajax_required, name='dispatch')
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
            if prev_album == album:
                return JsonResponse({'saved': 'No'})
            else:
                self.song.order = None
                self.song.album = album
                self.song.save()
            return JsonResponse({'saved': 'OK'})
        else:
            return HttpResponseForbidden()


@method_decorator(ajax_required, name='dispatch')
class AlbumCoverApplySongsView(LoginRequiredMixin, View):

    def post(self, request):
        album_id = request.POST.get('album_id')
        album = get_object_or_404(Album, user=request.user, id=album_id)
        album_cover = album.cover
        if album_cover:
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
class AlbumLikeView(LoginRequiredMixin, View):

    def post(self, request):
        album_id = request.POST.get('album_id')
        action = request.POST.get('action')

        album = get_object_or_404(Album, id=album_id)
        if album.name == '未分類專輯':
            return HttpResponseNotFound()

        if action == 'like':
            # prevent the error caused by user double like
            AlbumLikeShip.objects.get_or_create(user=request.user, album=album)
            album.total_likes = album.liked_by.count()
            album.save()
        else:
            AlbumLikeShip.objects.filter(user=request.user, album=album).delete()
            album.total_likes = album.liked_by.count()
            album.save()
        return JsonResponse({'saved': 'OK'})
