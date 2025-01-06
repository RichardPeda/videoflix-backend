from django.contrib import admin

from .models import Movie, MovieConvertables

# Register your models here.


admin.site.register(Movie)
admin.site.register(MovieConvertables)
