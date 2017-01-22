from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from ..forms import SongCreateForm
from django.contrib import messages
from ..models import Album, Song, SongLikeShip
from django.urls import reverse
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from playqueue.decorators import ajax_required


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