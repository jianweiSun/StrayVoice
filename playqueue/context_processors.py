from .playqueue import PlayQueue


def play_queue(request):
    return {'play_queue': PlayQueue(request)}
