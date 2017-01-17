from django import forms
from .models import FrontPageContent


class HeadPortraitUpdateForm(forms.ModelForm):
    class Meta:
        model = FrontPageContent
        fields = ('head_portrait', )
