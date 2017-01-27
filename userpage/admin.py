from django.contrib import admin
from .models import FrontPageContent


class FrontPageContentAdmin(admin.ModelAdmin):
    list_display = [f.name for f in FrontPageContent._meta.fields]


admin.site.register(FrontPageContent, FrontPageContentAdmin)
