from django.shortcuts import render
from django.views.generic.base import TemplateResponseMixin, View
from django.http import HttpResponseNotFound
from music.models import Song


class BrowseAllView(TemplateResponseMixin, View):
    template_name = 'browse/browse_all.html'

    def dispatch(self, request, *args, genre=None, order_type=None, **kwargs):
        genre_choice = {'0', '1', '2', '3', '4', 'all'}
        order_choice = {'latest', 'most_liked'}
        if genre not in genre_choice or order_type not in order_choice:
            return HttpResponseNotFound()
        return super(BrowseAllView, self).dispatch(request, *args, genre, order_type, **kwargs)

    def get(self, request, genre, order_type):
        queryset = Song.objects.filter(published=True)
        if genre != 'all':
            queryset = queryset.filter(genre=genre)

        if order_type == 'latest':
            queryset = queryset.order_by('-created', 'user')

        return self.render_to_response({'songs': queryset,
                                        'genre': genre,
                                        'order_type': order_type,
                                        'genre_list': ['all', '1', '2', '3', '4', '0'],
                                        'type_list': ['latest', 'most_liked']})
