from django.views.generic.base import TemplateResponseMixin, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound
from music.models import Song, Playlist
from accounts.models import FollowShip
from itertools import chain
from .utils import queryset_paging
from django.db.models import Count


class BrowseAllView(TemplateResponseMixin, View):
    template_name = 'browse/browse_all.html'

    def dispatch(self, request, *args, genre=None, order_type=None, **kwargs):
        genre_choice = {'0', '1', '2', '3', '4', 'all'}
        order_choice = {'latest', 'most_liked'}
        if genre not in genre_choice or order_type not in order_choice:
            return HttpResponseNotFound()
        return super(BrowseAllView, self).dispatch(request, *args, genre, order_type, **kwargs)

    def get(self, request, genre, order_type):
        queryset = Song.objects.filter(published=True).select_related('user__profile')
        if genre != 'all':
            queryset = queryset.filter(genre=genre)

        if order_type == 'latest':
            queryset = queryset.order_by('-created', 'user')
        elif order_type == 'most_liked':
            queryset = queryset.order_by('-total_likes', 'user')

        queryset = queryset_paging(request, queryset, 12)
        return self.render_to_response({'songs': queryset,
                                        'genre': genre,
                                        'order_type': order_type,
                                        'genre_list': ['all', '1', '2', '3', '4', '0'],
                                        'type_list': ['latest', 'most_liked']})


class BrowseLikeView(LoginRequiredMixin, TemplateResponseMixin, View):
    template_name = 'browse/browse_like.html'

    def dispatch(self, request, *args, genre=None, order_type=None, **kwargs):
        genre_choice = {'0', '1', '2', '3', '4', 'all'}
        order_choice = {'latest', 'most_liked', 'recent_liked'}
        if genre not in genre_choice or order_type not in order_choice:
            return HttpResponseNotFound()
        return super(BrowseLikeView, self).dispatch(request, *args, genre, order_type, **kwargs)

    def get(self, request, genre, order_type):
        queryset = request.user.like_songs.select_related('user__profile')
        if genre != 'all':
            queryset = queryset.filter(genre=genre)

        if order_type == 'latest':
            queryset = queryset.order_by('-created', 'user')
        elif order_type == 'most_liked':
            queryset = queryset.order_by('-total_likes', 'user')
        elif order_type == 'recent_liked':
            queryset = queryset.order_by('-songlikeship__created', 'user')

        queryset = queryset_paging(request, queryset, 12)
        return self.render_to_response({'songs': queryset,
                                        'genre': genre,
                                        'order_type': order_type,
                                        'genre_list': ['all', '1', '2', '3', '4', '0'],
                                        'type_list': ['latest', 'most_liked', 'recent_liked']})


class BrowseFollowView(LoginRequiredMixin, TemplateResponseMixin, View):
    template_name = 'browse/browse_follow.html'

    def dispatch(self, request, *args, genre=None, order_type=None, **kwargs):
        genre_choice = {'0', '1', '2', '3', '4', 'all'}
        order_choice = {'latest', 'most_liked', 'recent_followed'}
        if genre not in genre_choice or order_type not in order_choice:
            return HttpResponseNotFound()
        return super(BrowseFollowView, self).dispatch(request, *args, genre, order_type, **kwargs)

    def get(self, request, genre, order_type):
        following_list = FollowShip.objects.filter(profile_from=request.user.profile)\
                                           .values_list('profile_to__user', flat=True)
        queryset = Song.objects.filter(published=True).filter(user__in=following_list).select_related('user__profile')
        if genre != 'all':
            queryset = queryset.filter(genre=genre)

        if order_type == 'latest':
            queryset = queryset.order_by('-created', 'user')
        elif order_type == 'most_liked':
            queryset = queryset.order_by('-total_likes', 'user')
        # Combine the querysets so that we can use the same templates
        elif order_type == 'recent_followed':
            followship_obj = FollowShip.objects.filter(profile_from=request.user.profile).order_by('-created')
            if genre == 'all':
                queryset_by_user_list = [obj.profile_to.user.songs.all() for obj in followship_obj]
                queryset = list(chain.from_iterable(queryset_by_user_list))
            else:
                queryset_by_user_list = [obj.profile_to.user.songs.filter(genre=genre) for obj in followship_obj]
                queryset = list(chain.from_iterable(queryset_by_user_list))
        # to make pagination we must turn itertools.chain to list, so it has length
        queryset = queryset_paging(request, queryset, 12)
        return self.render_to_response({'songs': queryset,
                                        'genre': genre,
                                        'order_type': order_type,
                                        'genre_list': ['all', '1', '2', '3', '4', '0'],
                                        'type_list': ['latest', 'most_liked', 'recent_followed']})


class PlaylistBrowseAllView(TemplateResponseMixin, View):
    template_name = "browse/playlist_browse_all.html"

    def dispatch(self, request, *args, order_type=None, **kwargs):
        order_choice = {'latest', 'most_liked'}
        if order_type not in order_choice:
            return HttpResponseNotFound()
        return super(PlaylistBrowseAllView, self).dispatch(request, *args, order_type, **kwargs)

    def get(self, request, order_type):
        playlists = Playlist.objects.annotate(songs_number=Count('songs'))\
                                    .filter(published=True).exclude(songs_number=0)

        if order_type == 'latest':
            playlists = playlists.order_by('-created', 'user')
        else:
            playlists = playlists.order_by('-total_likes', 'user')

        playlists = queryset_paging(request, playlists, 8)
        return self.render_to_response({'items': playlists,
                                        'order_type': order_type,
                                        'type_list': ['latest', 'most_liked']})


class PlaylistBrowseMineView(LoginRequiredMixin, TemplateResponseMixin, View):
    template_name = "browse/playlist_browse_mine.html"

    def dispatch(self, request, *args, order_type=None, **kwargs):
        order_choice = {'latest', 'most_liked'}
        if order_type not in order_choice:
            return HttpResponseNotFound()
        return super(PlaylistBrowseMineView, self).dispatch(request, *args, order_type, **kwargs)

    def get(self, request, order_type):
        playlists = Playlist.objects.annotate(songs_number=Count('songs'))\
                                    .filter(user=request.user, published=True).exclude(songs_number=0)

        if order_type == 'latest':
            playlists = playlists.order_by('-created', 'user')
        else:
            playlists = playlists.order_by('-total_likes', 'user')

        playlists = queryset_paging(request, playlists, 8)
        return self.render_to_response({'items': playlists,
                                        'order_type': order_type,
                                        'type_list': ['latest', 'most_liked']})


class PlaylistBrowseLikeView(LoginRequiredMixin, TemplateResponseMixin, View):
    template_name = "browse/playlist_browse_like.html"

    def dispatch(self, request, *args, order_type=None, **kwargs):
        order_choice = {'latest', 'most_liked', 'recent_liked'}
        if order_type not in order_choice:
            return HttpResponseNotFound()
        return super(PlaylistBrowseLikeView, self).dispatch(request, *args, order_type, **kwargs)

    def get(self, request, order_type):
        playlists = request.user.like_playlists.annotate(songs_number=Count('songs'))\
                                               .filter(published=True).exclude(songs_number=0)

        if order_type == 'latest':
            playlists = playlists.order_by('-created', 'user')
        elif order_type == 'most_liked':
            playlists = playlists.order_by('-total_likes', 'user')
        else:
            playlists = playlists.order_by('-playlistlikeship__created', 'user')

        playlists = queryset_paging(request, playlists, 8)
        return self.render_to_response({'items': playlists,
                                        'order_type': order_type,
                                        'type_list': ['latest', 'most_liked', 'recent_liked']})


class PlaylistBrowseFollowView(LoginRequiredMixin, TemplateResponseMixin, View):
    template_name = "browse/playlist_browse_like.html"

    def dispatch(self, request, *args, order_type=None, **kwargs):
        order_choice = {'latest', 'most_liked', 'recent_followed'}
        if order_type not in order_choice:
            return HttpResponseNotFound()
        return super(PlaylistBrowseFollowView, self).dispatch(request, *args, order_type, **kwargs)

    def get(self, request, order_type):
        following_list = FollowShip.objects.filter(profile_from=request.user.profile)\
                                           .values_list('profile_to__user', flat=True)
        playlists = Playlist.objects.annotate(songs_number=Count('songs'))\
                                    .filter(published=True, user__in=following_list).exclude(songs_number=0)

        if order_type == 'latest':
            playlists = playlists.order_by('-created', 'user')
        elif order_type == 'most_liked':
            playlists = playlists.order_by('-total_likes', 'user')
        else:
            playlists = playlists.order_by('-playlistlikeship__created', 'user')

        playlists = queryset_paging(request, playlists, 8)
        return self.render_to_response({'items': playlists,
                                        'order_type': order_type,
                                        'type_list': ['latest', 'most_liked', 'recent_liked']})

