from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View, TemplateResponseMixin
from django.contrib.auth.models import User
from .forms import HeadPortraitUpdateForm
from browse.utils import queryset_paging
from django.http import HttpResponseNotFound
from django.db.models import Sum, Case, When, IntegerField


def get_tmp_homepage(request):
    return render(request, 'tmp_home_page.html')


class FrontPageView(TemplateResponseMixin, View):
    template_name = 'userpage/front_page_music.html'

    def dispatch(self, request, *args, username=None, **kwargs):
        self.user = get_object_or_404(User, username=username)
        self.albums = self.user.albums.exclude(name='未分類專輯') \
                               .annotate(songs_number=Sum(Case(When(songs__published=True, then=1),
                                                               output_field=IntegerField()))
                                         ) \
                               .exclude(songs_number=0)
        self.unalbum = self.user.albums.filter(name='未分類專輯') \
                                .annotate(songs_number=Sum(Case(When(songs__published=True, then=1),
                                                                output_field=IntegerField()))
                                          ) \
                                .exclude(songs_number=0).first()
        return super(FrontPageView, self).dispatch(request, *args, username, **kwargs)

    def get(self, request, username):
        if self.user == request.user:
            form = HeadPortraitUpdateForm(instance=request.user.frontpagecontent)
            return self.render_to_response({'user': self.user,
                                            'form': form,
                                            'albums': self.albums,
                                            'unalbum': self.unalbum,
                                            'section': 'music'})
        else:
            return self.render_to_response({'user': self.user,
                                            'albums': self.albums,
                                            'unalbum': self.unalbum,
                                            'section': 'music'})

    def post(self, request, username):
        form = HeadPortraitUpdateForm(instance=request.user.frontpagecontent,
                                      files=request.FILES)
        if form.is_valid():
            form.save()

        return self.render_to_response({'user': self.user,
                                        'form': form,
                                        'albums': self.albums,
                                        'unalbum': self.unalbum,
                                        'section': 'music'})


class FrontPagePlaylistView(TemplateResponseMixin, View):
    template_name = 'userpage/front_page_playlist.html'

    def dispatch(self, request, *args, username=None, order_type=None, **kwargs):
        order_choice = {'latest', 'most_liked'}
        if order_type not in order_choice:
            return HttpResponseNotFound()

        self.user = get_object_or_404(User, username=username)
        self.playlists = self.user.playlists.filter(published=True) \
                                  .annotate(songs_number=Sum(Case(When(songs__published=True, then=1),
                                                                  output_field=IntegerField()))
                                            ) \
                                  .exclude(songs_number=0).select_related('user__profile')
        return super(FrontPagePlaylistView, self).dispatch(request, *args, username, order_type, **kwargs)

    def get(self, request, username, order_type):
        if order_type == 'latest':
            playlists = self.playlists.order_by('-created')
        else:
            playlists = self.playlists.order_by('-total_likes', 'user')

        playlists = queryset_paging(request, playlists, 8)
        return self.render_to_response({'user': self.user,
                                        'playlists': playlists,
                                        'order_type': order_type,
                                        'type_list': ['latest', 'most_liked'],
                                        'section': 'playlist'})


class FrontPageAboutFollowingsView(TemplateResponseMixin, View):
    template_name = 'userpage/front_page_about_followings.html'

    def dispatch(self, request, *args, username=None, **kwargs):
        self.user = get_object_or_404(User, username=username)
        return super(FrontPageAboutFollowingsView, self).dispatch(request, *args, username, **kwargs)

    def get(self, request, username):
        followings = self.user.profile.followings.order_by('-follow_to_set__created')
        return self.render_to_response({'user': self.user,
                                        'followings': followings,
                                        'section': 'about'})


class FrontPageAboutFollowersView(TemplateResponseMixin, View):
    template_name = 'userpage/front_page_about_followers.html'

    def dispatch(self, request, *args, username=None, **kwargs):
        self.user = get_object_or_404(User, username=username)
        return super(FrontPageAboutFollowersView, self).dispatch(request, *args, username, **kwargs)

    def get(self, request, username):
        followers = self.user.profile.followers.order_by('-follow_from_set__created')
        return self.render_to_response({'user': self.user,
                                        'followers': followers,
                                        'section': 'about'})

