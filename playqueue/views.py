from django.shortcuts import render, get_object_or_404
from .playqueue import PlayQueue
from django.views.generic.base import View, TemplateResponseMixin
from music.models import Song, Album
from django.utils.decorators import method_decorator
from .decorators import ajax_required
from django.http import JsonResponse, HttpResponseBadRequest
import json


@method_decorator(ajax_required, name='dispatch')
class PlayQueuePrepend(TemplateResponseMixin, View):
    template_name = 'playqueue/queue_song.html'

    def get(self, request, song_id):
        song = get_object_or_404(Song, id=song_id)
        queue = PlayQueue(request)
        queue.prepend(song)
        return self.render_to_response({'song': song})


@method_decorator(ajax_required, name='dispatch')
class PlayQueueAppend(TemplateResponseMixin, View):
    template_name = 'playqueue/queue_song.html'

    def get(self, request, song_id):
        song = get_object_or_404(Song, id=song_id)
        queue = PlayQueue(request)
        queue.append(song)
        return self.render_to_response({'song': song})


@method_decorator(ajax_required, name='dispatch')
class PlayQueueRemove(View):

    def get(self, request, index):
        index_num = int(index)
        queue = PlayQueue(request)
        if index_num > len(queue.queue):
            return HttpResponseBadRequest()
        else:
            queue.remove(index_num)
        return JsonResponse({'saved': 'OK'})


@method_decorator(ajax_required, name='dispatch')
class PlayQueueClear(View):

    def get(self, request):
        queue = PlayQueue(request)
        queue.clear()
        return JsonResponse({'saved': 'OK'})


@method_decorator(ajax_required, name='dispatch')
class PlayQueueExchange(TemplateResponseMixin, View):
    template_name = 'playqueue/queue_songs.html'

    def get(self, request):
        ids_list = json.loads(request.GET['ids_list'])
        queue = PlayQueue(request)
        queue.exchange(ids_list)
        return self.render_to_response({'queue': queue})


@method_decorator(ajax_required, name='dispatch')
class AlbumSongsExchange(TemplateResponseMixin, View):
    template_name = 'playqueue/queue_songs.html'

    def get(self, request, album_id):
        album = get_object_or_404(Album, id=album_id)
        ids_lists = list(album.songs.values_list('id', flat=True).order_by('order'))
        queue = PlayQueue(request)
        queue.exchange(ids_lists)
        return self.render_to_response({'queue': queue})

