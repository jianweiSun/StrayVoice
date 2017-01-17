from django.shortcuts import render
from .forms import LoginForm, RegistrationForm, ProfileEditForm, \
    EmailEditForm, PasswordEditForm, AccountDeleteForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.views.generic.base import View, TemplateResponseMixin
from .models import Profile
from userpage.models import FrontPageContent
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib.auth.views import _get_login_redirect_url
from music.models import Album


def user_login(request):
    # refer to auth.views.login
    redirect_to = request.POST.get('next', request.GET.get('next', ''))
    redirect_to = _get_login_redirect_url(request, redirect_to)

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'],
                                password=cd['password'])
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(redirect_to)
            else:
                messages.error(request, '登入失敗，請輸入正確的帳號及密碼')

    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


class RegistrationView(TemplateResponseMixin, View):
    template_name = 'accounts/registration.html'

    def get(self, request):
        form = RegistrationForm()
        return self.render_to_response({'form': form})

    def post(self, request):
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_user = form.save(commit=False)
            new_user.set_password(cd['password'])
            new_user.save()
            # bind model instance which is needed for new_user
            Profile.objects.create(user=new_user, nickname=cd['nickname'])
            FrontPageContent.objects.create(user=new_user)
            # create default album for new_user
            Album.objects.create(user=new_user, name='未分類專輯')
            messages.success(request, '成功註冊，請使用以下表格登入')
            return redirect(reverse('login'))
        else:
            return self.render_to_response({'form': form})


class ProfileEditView(TemplateResponseMixin, LoginRequiredMixin, View):
    template_name = 'accounts/profile_edit.html'

    def get(self, request):
        form = ProfileEditForm(instance=request.user.profile)
        return self.render_to_response({'form': form,
                                        'section': 'profile_edit'})

    def post(self, request):
        form = ProfileEditForm(instance=request.user.profile,
                               data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '更新成功')
        else:
            messages.error(request, '更新失敗')
        return self.render_to_response({'form': form,
                                        'section': 'profile_edit'})


class EmailEditView(TemplateResponseMixin, LoginRequiredMixin, View):
    template_name = 'accounts/email_edit.html'

    def get(self, request):
        form = EmailEditForm()
        return self.render_to_response({'form': form,
                                        'section': 'email_edit'})

    def post(self, request):
        form = EmailEditForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data['email']
            user = request.user
            if user.email == cd:
                messages.error(request, '新的電子郵件與原本的電子郵件相同')
                # render empty form
                form = EmailEditForm()
            else:
                user.email = cd
                user.save()
                messages.success(request, '更新成功')
                # if it's success render empty form
                form = EmailEditForm()
        else:
            messages.error(request, '更新失敗')
        return self.render_to_response({'form': form, 'section': 'email_edit'})


class PasswordEditView(TemplateResponseMixin, LoginRequiredMixin, View):
    template_name = 'accounts/password_edit.html'

    def get(self, request):
        form = PasswordEditForm()
        return self.render_to_response({'form': form,
                                        'section': 'password_edit'})

    def post(self, request):
        form = PasswordEditForm(request.POST)
        if form.is_valid():
            user = request.user
            cd = form.cleaned_data
            if not user.check_password(cd['old']):
                messages.error(request, '舊密碼輸入錯誤')
            else:
                user.set_password(cd['new'])
                user.save()
                messages.success(request, '更新成功')
                user = authenticate(username=user.username,
                                    password=cd['new'])
                login(request, user)

        else:
            messages.error(request, '更新失敗')
        return self.render_to_response({'form': form,
                                        'section': 'password_edit'})


class AccountDeleteView(TemplateResponseMixin, LoginRequiredMixin, View):
    template_name = 'accounts/account_delete.html'

    def get(self, request):
        form = AccountDeleteForm()
        return self.render_to_response({'form': form,
                                        'section': 'account_delete'})

    def post(self, request):
        form = AccountDeleteForm(request.POST)
        if form.is_valid():
            user = request.user
            user.delete()
            messages.success(request, '您的帳號已經成功刪除')
            logout(request)
            return redirect(reverse('login'))
        else:
            messages.error(request, '刪除失敗')
        return self.render_to_response({'form': form,
                                        'section': 'account_delete'})
