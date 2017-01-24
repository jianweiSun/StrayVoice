from django import forms
from django.contrib.auth.models import User
from .models import Profile
import re


class LoginForm(forms.Form):
    username = forms.CharField(min_length=3, max_length=30)
    password = forms.CharField(widget=forms.PasswordInput,
                               min_length=6, max_length=30)


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label='密碼', label_suffix=' ', min_length=6,
                               max_length=30, widget=forms.PasswordInput)
    password2 = forms.CharField(label='密碼確認', label_suffix=' ', min_length=6,
                                max_length=30, widget=forms.PasswordInput)
    nickname = forms.CharField(label='暱稱/顯示名稱', label_suffix=' ')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        email = self.fields['email']
        username = self.fields['username']
        email.required = True
        email.label_suffix = ' '
        username.label_suffix = ' '

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('兩次輸入密碼不相符')
        return cd['password2']

    def clean_username(self):
        cleaned_username = self.cleaned_data['username']
        if not re.match('^[\w]+$', cleaned_username):
            raise forms.ValidationError('請輸入僅由英文字母及數字建立的帳號名稱')
        if len(cleaned_username) > 30 or len(cleaned_username) < 3:
            raise forms.ValidationError('有效帳號長度介於3至30字元之間')
        return cleaned_username

    class Meta:
        model = User
        fields = ('username', 'email')
        labels = {
            'username': '帳號',
        }
        help_texts = {
            'username': '',
        }


class ProfileEditForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)
        self.fields['realname'].label_suffix = ' '
        self.fields['nickname'].label_suffix = ' '

    class Meta:
        model = Profile
        fields = ('realname', 'nickname')


class EmailEditForm(forms.Form):
    email = forms.EmailField(max_length=50, label_suffix=' ', label='新的電子郵件')
    email_confirm = forms.EmailField(max_length=50, label_suffix=' ', label='再輸入一次')

    def clean_email_confirm(self):
        cd = self.cleaned_data
        if cd['email'] != cd['email_confirm']:
            raise forms.ValidationError('兩次輸入電子郵件不相符')
        return cd['email_confirm']


class PasswordEditForm(forms.Form):
    old = forms.CharField(widget=forms.PasswordInput, min_length=6,
                          max_length=30, label='舊密碼', label_suffix=' ')
    new = forms.CharField(widget=forms.PasswordInput, min_length=6,
                          max_length=30,  label='新密碼', label_suffix=' ')
    new_confirm = forms.CharField(widget=forms.PasswordInput, min_length=6,
                                  max_length=30,  label='再輸入一次', label_suffix=' ')

    def clean_new(self):
        cd = self.cleaned_data
        if cd['old'] == cd['new']:
            raise forms.ValidationError('新密碼與舊密碼相同')
        return cd['new']

    def clean_new_confirm(self):
        cd = self.cleaned_data
        # if clean_new raise error, you will not find cd['new'] cause it's not return
        new_password = cd.get('new', None)
        if new_password and new_password != cd['new_confirm']:
            raise forms.ValidationError('兩次輸入密碼不相符')
        return cd['new_confirm']


class AccountDeleteForm(forms.Form):
    confirm_message = forms.CharField(label='請輸入： 我已確認要刪除帳號', label_suffix=' ',
                                      max_length=15)

    def clean_confirm_message(self):
        confirm_message = self.cleaned_data['confirm_message']
        if confirm_message != '我已確認要刪除帳號':
            raise forms.ValidationError('確認訊息輸入錯誤')
        return confirm_message
