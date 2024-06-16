from django.contrib import admin

from .models import Photo


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'upload_date')
    search_fields = ('title', 'description')
    list_filter = ('upload_date', 'user')


