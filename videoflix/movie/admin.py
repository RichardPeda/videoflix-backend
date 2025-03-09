from django.contrib import admin

from .models import Movie, MovieConvertables, ConnectionTestFile, MovieProgress

# Register your models here.


admin.site.register(Movie)
admin.site.register(MovieConvertables)
admin.site.register(ConnectionTestFile)
admin.site.register(MovieProgress)
