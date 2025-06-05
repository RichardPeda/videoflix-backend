from django.contrib import admin
from django.utils.html import format_html
from .forms import MovieAdminForm
from .models import Movie, MovieConvertables, ConnectionTestFile, MovieProgress

admin.site.register(ConnectionTestFile)
admin.site.register(MovieProgress)

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    form = MovieAdminForm
    list_display = ('id', 'title', 'genre', 'rating', 'ranking', 'thumbnail_preview')
    readonly_fields = ('thumbnail_preview', 'image_file', 'duration')

    def thumbnail_preview(self, obj):
        if obj.image_file:
            return format_html(
                '<img src="{}" style="height:100px; object-fit: cover;" />',
                obj.image_file.url
            )
        return "-"
    thumbnail_preview.short_description = "Preview"

@admin.register(MovieConvertables)
class MovieConvertableAdmin(admin.ModelAdmin):
    list_display = ('id', 'movie')
