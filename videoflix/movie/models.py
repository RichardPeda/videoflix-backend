from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=30)
    genre = models.CharField(max_length=30, default='')
    rating = models.IntegerField(default=12)
    ranking = models.DecimalField(decimal_places=1, max_digits=4, default=0.0)
    duration = models.FloatField()
    image_url = models.FileField(upload_to='uploads/images/', null=True, blank=True)
    video_url = models.FileField(upload_to='uploads/videos/', null=True, blank=True)
    
class MovieConvertables(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_convertables')
    video_120p = models.FileField(upload_to='uploads/videos/', null=True, blank=True)
    video_360p = models.FileField(upload_to='uploads/videos/', null=True, blank=True)
    video_720p = models.FileField(upload_to='uploads/videos/', null=True, blank=True)
    video_1080p = models.FileField(upload_to='uploads/videos/', null=True, blank=True)