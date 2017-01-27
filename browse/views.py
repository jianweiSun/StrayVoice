from django.views.generic.base import TemplateResponseMixin, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound
from music.models import Song, Playlist, Album
from accounts.models import FollowShip
from itertools import chain
from .utils import queryset_paging
from django.db.models import Sum, IntegerField, Case, When


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
            queryset = queryset.order_by('-created')
        else:
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
        queryset = request.user.like_songs.filter(published=True).select_related('user__profile')
        if genre != 'all':
            queryset = queryset.filter(genre=genre)

        if order_type == 'latest':
            queryset = queryset.order_by('-created')
        elif order_type == 'most_liked':
            queryset = queryset.order_by('-total_likes', 'user')
        else:
            queryset = queryset.order_by('-songlikeship__created')

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
            queryset = queryset.order_by('-created')
        elif order_type == 'most_liked':
            queryset = queryset.order_by('-total_likes', 'user')
        # Combine the querysets so that we can use the same templates
        else:
            followship_obj = FollowShip.objects.filter(profile_from=request.user.profile).order_by('-created')
            # to make pagination we must turn itertools.chain to list, so it has length
            if genre == 'all':
                queryset_by_individual_list = [obj.profile_to.user.songs.filter(published=True)
                                                  .select_related('user__profile') for obj in followship_obj]
                queryset = list(chain.from_iterable(queryset_by_individual_list))
            else:
                queryset_by_user_list = [obj.profile_to.user.songs.filter(genre=genre, published=True)
                                            .select_related('user__profile') for obj in followship_obj]
                queryset = list(chain.from_iterable(queryset_by_user_list))

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
        playlists = Playlist.objects.filter(published=True)\
                            .annotate(songs_number=Sum(Case(When(songs__published=True, then=1),
                                                            output_field=IntegerField()))
                                      )\
                            .exclude(songs_number=0).select_related('user__profile')

        if order_type == 'latest':
            playlists = playlists.order_by('-created')
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
        # able to browse un-published playlist of yourself
        playlists = Playlist.objects.filter(user=request.user)\
                            .annotate(songs_number=Sum(Case(When(songs__published=True, then=1),
                                                            output_field=IntegerField()))
                                      )\
                            .exclude(songs_number=0).select_related('user__profile')

        if order_type == 'latest':
            playlists = playlists.order_by('-created')
        else:
            playlists = playlists.order_by('-total_likes')

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
        playlists = request.user.like_playlists.filter(published=True) \
                           .annotate(songs_number=Sum(Case(When(songs__published=True, then=1),
                                                           output_field=IntegerField()))
                                     ) \
                           .exclude(songs_number=0).select_related('user__profile')

        if order_type == 'latest':
            playlists = playlists.order_by('-created')
        elif order_type == 'most_liked':
            playlists = playlists.order_by('-total_likes', 'user')
        else:
            playlists = playlists.order_by('-playlistlikeship__created')

        playlists = queryset_paging(request, playlists, 8)
        return self.render_to_response({'items': playlists,
                                        'order_type': order_type,
                                        'type_list': ['latest', 'most_liked', 'recent_liked']})


class PlaylistBrowseFollowView(LoginRequiredMixin, TemplateResponseMixin, View):
    template_name = "browse/playlist_browse_follow.html"

    def dispatch(self, request, *args, order_type=None, **kwargs):
        order_choice = {'latest', 'most_liked', 'recent_followed'}
        if order_type not in order_choice:
            return HttpResponseNotFound()
        return super(PlaylistBrowseFollowView, self).dispatch(request, *args, order_type, **kwargs)

    def get(self, request, order_type):
        following_list = FollowShip.objects.filter(profile_from=request.user.profile)\
                                           .values_list('profile_to__user', flat=True)
        playlists = Playlist.objects.filter(published=True, user__in=following_list) \
                            .annotate(songs_number=Sum(Case(When(songs__published=True, then=1),
                                                            output_field=IntegerField()))
                                      ) \
                            .exclude(songs_number=0).select_related('user__profile')
        # to make pagination we must turn itertools.chain to list, so it has length
        if order_type == 'latest':
            playlists = playlists.order_by('-created')
        elif order_type == 'most_liked':
            playlists = playlists.order_by('-total_likes', 'user')
        else:
            followship_obj = FollowShip.objects.filter(profile_from=request.user.profile).order_by('-created')
            playlists_by_individual_list = [obj.profile_to.user.playlists.filter(published=True)
                                               .annotate(songs_number=Sum(Case(When(songs__published=True, then=1),
                                                                               output_field=IntegerField()))
                                                         )
                                               .exclude(songs_number=0)
                                               .select_related('user__profile') for obj in followship_obj]
            playlists = list(chain.from_iterable(playlists_by_individual_list))

        playlists = queryset_paging(request, playlists, 8)
        return self.render_to_response({'items': playlists,
                                        'order_type': order_type,
                                        'type_list': ['latest', 'most_liked', 'recent_followed']})


class AlbumBrowseAllView(TemplateResponseMixin, View):
    template_name = "browse/album_browse_all.html"

    def dispatch(self, request, *args, order_type=None, **kwargs):
        order_choice = {'latest', 'most_liked'}
        if order_type not in order_choice:
            return HttpResponseNotFound()
        return super(AlbumBrowseAllView, self).dispatch(request, *args, order_type, **kwargs)

    def get(self, request, order_type):
        albums = Album.objects.exclude(name='未分類專輯') \
                      .annotate(songs_number=Sum(Case(When(songs__published=True, then=1),
                                                      output_field=IntegerField()))
                                ) \
                      .exclude(songs_number=0).select_related('user__profile')

        if order_type == 'latest':
            albums = albums.order_by('-created')
        else:
            albums = albums.order_by('-total_likes', 'user')

        albums = queryset_paging(request, albums, 8)
        return self.render_to_response({'items': albums,
                                        'order_type': order_type,
                                        'type_list': ['latest', 'most_liked']})


class AlbumBrowseMineView(LoginRequiredMixin, TemplateResponseMixin, View):
    template_name = "browse/album_browse_mine.html"

    def dispatch(self, request, *args, order_type=None, **kwargs):
        order_choice = {'latest', 'most_liked'}
        if order_type not in order_choice:
            return HttpResponseNotFound()
        return super(AlbumBrowseMineView, self).dispatch(request, *args, order_type, **kwargs)

    def get(self, request, order_type):
        albums = Album.objects.filter(user=request.user).exclude(name='未分類專輯') \
                      .annotate(songs_number=Sum(Case(When(songs__published=True, then=1),
                                                      output_field=IntegerField()))
                                ) \
                      .exclude(songs_number=0).select_related('user__profile')

        if order_type == 'latest':
            albums = albums.order_by('-created')
        else:
            albums = albums.order_by('-total_likes')

        albums = queryset_paging(request, albums, 8)
        return self.render_to_response({'items': albums,
                                        'order_type': order_type,
                                        'type_list': ['latest', 'most_liked']})


class AlbumBrowseLikeView(LoginRequiredMixin, TemplateResponseMixin, View):
    template_name = "browse/album_browse_like.html"

    def dispatch(self, request, *args, order_type=None, **kwargs):
        order_choice = {'latest', 'most_liked', 'recent_liked'}
        if order_type not in order_choice:
            return HttpResponseNotFound()
        return super(AlbumBrowseLikeView, self).dispatch(request, *args, order_type, **kwargs)

    def get(self, request, order_type):
        albums = request.user.like_albums \
                        .annotate(songs_number=Sum(Case(When(songs__published=True, then=1),
                                                        output_field=IntegerField()))
                                  ) \
                        .exclude(songs_number=0).select_related('user__profile')

        if order_type == 'latest':
            albums = albums.order_by('-created')
        elif order_type == 'most_liked':
            albums = albums.order_by('-total_likes', 'user')
        else:
            albums = albums.order_by('-albumlikeship__created')

        albums = queryset_paging(request, albums, 8)
        return self.render_to_response({'items': albums,
                                        'order_type': order_type,
                                        'type_list': ['latest', 'most_liked', 'recent_liked']})


class AlbumBrowseFollowView(LoginRequiredMixin, TemplateResponseMixin, View):
    template_name = "browse/album_browse_follow.html"

    def dispatch(self, request, *args, order_type=None, **kwargs):
        order_choice = {'latest', 'most_liked', 'recent_followed'}
        if order_type not in order_choice:
            return HttpResponseNotFound()
        return super(AlbumBrowseFollowView, self).dispatch(request, *args, order_type, **kwargs)

    def get(self, request, order_type):
        following_list = FollowShip.objects.filter(profile_from=request.user.profile)\
                                           .values_list('profile_to__user', flat=True)
        albums = Album.objects.filter(user__in=following_list).exclude(name='未分類專輯') \
                      .annotate(songs_number=Sum(Case(When(songs__published=True, then=1),
                                                      output_field=IntegerField()))
                                ) \
                      .exclude(songs_number=0).select_related('user__profile')
        # to make pagination we must turn itertools.chain to list, so it has length
        if order_type == 'latest':
            albums = albums.order_by('-created')
        elif order_type == 'most_liked':
            albums = albums.order_by('-total_likes', 'user')
        else:
            followship_obj = FollowShip.objects.filter(profile_from=request.user.profile).order_by('-created')
            albums_by_individual_list = [obj.profile_to.user.albums.exclude(name='未分類專輯')
                                            .annotate(songs_number=Sum(Case(When(songs__published=True, then=1),
                                                                            output_field=IntegerField()))
                                                      )
                                            .select_related('user__profile') for obj in followship_obj]
            albums = list(chain.from_iterable(albums_by_individual_list))

        albums = queryset_paging(request, albums, 8)
        return self.render_to_response({'items': albums,
                                        'order_type': order_type,
                                        'type_list': ['latest', 'most_liked', 'recent_followed']})


class SearchView(TemplateResponseMixin, View):
    template_name = 'browse/search.html'

    def get(self, request):
        query_str = request.GET.get('q')
        if query_str:
            songs = Song.objects.filter(name__icontains=query_str)
        else:
            songs = None
        return self.render_to_response({'query_str': query_str,
                                        'songs': songs})
