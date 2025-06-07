from django.contrib import admin
from django.utils.html import format_html
from .forms import MovieAdminForm
from .models import Movie, MovieConvertables, ConnectionTestFile, MovieProgress

admin.site.register(ConnectionTestFile)
admin.site.register(MovieProgress)

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """
    Customize admin view for model Movie in the Django admin interface.

    This class registers a custom ModelAdmin for the Movie model to configure its behavior
    in the Django admin panel.

    Key features:
    - Uses a custom form (MovieAdminForm) for validation and field customization.
    - Displays specific fields in the list view: ID, title, genre, rating, ranking, and a thumbnail preview.
    - Marks some fields as read-only in the detail view: thumbnail preview, image file, and duration.
    - Implements a custom method `thumbnail_preview` to show a 100px-tall image preview
    (if an image is available) using inline HTML in both the list and detail views.

    Attributes:
    - form: Specifies the custom form used for the model.
    - list_display: Fields shown in the changelist (overview) view.
    - readonly_fields: Fields disabled for editing in the detail view.

    Methods:
    - thumbnail_preview(obj): Returns a formatted HTML image element if an image exists;
    otherwise, returns a dash ("-"). Used both as a column in the list view and a read-only field.

    Note:
    - The thumbnail is styled with a fixed height and object-fit: cover to ensure uniform appearance.
    - The short_description "Preview" is used as the label in the admin interface.
    """

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
    """
    Customize admin view for model MovieConvertables in the Django admin interface.

    This class registers a custom ModelAdmin for the MovieConvertables model to define
    its behavior in the Django admin panel.

    Key features:
    - Registers the MovieConvertables model with a minimal configuration.
    - Displays the fields 'id' and 'movie' in the list (changelist) view.

    Attributes:
    - list_display: Defines the fields shown in the admin list view for each MovieConvertables entry.
    """
    list_display = ('id', 'movie')
