from django import forms
from .models import Song, Album, Playlist
from .validators import validate_mp3


class SongCreateForm(forms.ModelForm):
    # field order = [...]
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(SongCreateForm, self).__init__(*args, **kwargs)
        self.fields['album'] = forms.ModelChoiceField(queryset=Album.objects.filter(user=user),
                                                      initial=user.albums.get(name='未分類專輯'))
        self.fields['file'].validators = [validate_mp3, ]

    class Meta:
        model = Song
        exclude = ['user', 'album', 'created', 'order', 'liked_by', 'total_likes']
        widgets = {
            'length': forms.HiddenInput,
        }


class AlbumCreateForm(forms.ModelForm):

    def clean_name(self):
        cd = self.cleaned_data
        if cd['name'] == '未分類專輯':
            raise forms.ValidationError('該名稱為系統預設，無法使用')
        return cd['name']

    class Meta:
        model = Album
        fields = ('cover', 'name', 'description')


class SongChangeAlbumForm(forms.Form):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(SongChangeAlbumForm, self).__init__(*args, **kwargs)
        self.fields['album'] = forms.ModelChoiceField(queryset=Album.objects.filter(user=user),
                                                      initial=user.albums.get(name='未分類專輯'))


class PlaylistCreateForm(forms.ModelForm):

    class Meta:
        model = Playlist
        fields = ('cover', 'name', 'description', 'published')
