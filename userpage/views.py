from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View, TemplateResponseMixin
from django.contrib.auth.models import User
from .forms import HeadPortraitUpdateForm
from django.contrib import messages


def get_tmp_homepage(request):
    return render(request, 'tmp_home_page.html')


class FrontPageView(TemplateResponseMixin, View):
    template_name = 'userpage/front_page.html'

    def dispatch(self, request, username):
        self.user = get_object_or_404(User, username=username)
        return super(FrontPageView, self).dispatch(request, username)

    def get(self, request, username):
        if self.user == request.user:
            form = HeadPortraitUpdateForm(instance=request.user.frontpagecontent)
            return self.render_to_response({'user': self.user,
                                            'form': form})
        else:
            return self.render_to_response({'user': self.user})

    def post(self, request, username):
        form = HeadPortraitUpdateForm(instance=request.user.frontpagecontent,
                                      files=request.FILES)
        if form.is_valid():
            # try to delete old file, but still got bug while rendering, try signal
            # self.user.frontpagecontent.head_portrait.delete(save=False)
            form.save()
        else:
            messages.error(request, '照片上傳失敗')
        return self.render_to_response({'user': self.user,
                                        'form': form})

