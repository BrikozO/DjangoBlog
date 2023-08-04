from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from .models import Profile


# Register your models here.
@admin.register(Profile)
class MyProfile(SummernoteModelAdmin):
    summernote_fields = ('bio',)
