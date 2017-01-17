from django.conf import settings
from music.models import Song


class PlayQueue(object):

    def __init__(self, request):
        self.session = request.session
        # queue reference to 'playqueue' in session
        queue = self.session.get(settings.PLAY_QUEUE_SESSION_ID)
        if not queue:
            self.session[settings.PLAY_QUEUE_SESSION_ID] = []
            queue = self.session[settings.PLAY_QUEUE_SESSION_ID]
        self.queue = queue

    def append(self, song):
        self.queue.append(song.id)
        self.save()

    def prepend(self, song):
        self.queue.insert(0, song.id)
        self.save()

    def extend(self, ids_list):
        self.queue.extend(ids_list)
        self.save()

    def exchange(self, ids_list):
        self.session[settings.PLAY_QUEUE_SESSION_ID] = ids_list
        self.queue = self.session[settings.PLAY_QUEUE_SESSION_ID]
        self.save()

    def remove(self, index):
        if index < len(self.queue):
            del self.queue[index]
            self.save()

    def clear(self):
        del self.session[settings.PLAY_QUEUE_SESSION_ID]
        self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        songs_bulk = Song.objects.in_bulk(self.queue)
        for song_id in self.queue:
            yield songs_bulk[song_id]
