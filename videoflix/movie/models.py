from django.db import models
from django.utils.timezone import now

from userprofile.models import CustomUser

class Movie(models.Model):
    GENRE_CHOICES = {
        "NEW": "New",
        "ACTION": "Action",
        "DOCUMENTARY": "Documentary",
        "ROMANTIC": "Romantic",
        "DRAMA": "Drama",
    }

    title = models.CharField(max_length=30)
    description = models.CharField(max_length=500)
    genre = models.CharField(max_length=30, choices=GENRE_CHOICES, default="NEW")
    rating = models.IntegerField(default=0)
    ranking = models.DecimalField(decimal_places=1, max_digits=4, default=0.0)
    duration = models.FloatField(default=0.0)
    image_url = models.FileField(upload_to='uploads/images/', null=True, blank=True)
    video_url = models.FileField(upload_to='uploads/videos/', null=True, blank=True)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.id} {self.title}"
    
class MovieConvertables(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_convertables')
    video_120p = models.FileField(upload_to='uploads/videos/', null=True, blank=True)
    video_360p = models.FileField(upload_to='uploads/videos/', null=True, blank=True)
    video_720p = models.FileField(upload_to='uploads/videos/', null=True, blank=True)
    video_1080p = models.FileField(upload_to='uploads/videos/', null=True, blank=True)

class MovieProgress(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_progress')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    time = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

class ConnectionTestFile(models.Model):
    file = models.FileField(upload_to='uploads/testfile/', null=True, blank=True)