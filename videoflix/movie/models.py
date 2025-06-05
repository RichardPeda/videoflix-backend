from django.db import models
from django.utils.timezone import now
from django.core.validators import MinValueValidator, MaxValueValidator

from userprofile.models import CustomUser

class Movie(models.Model):
    GENRE_CHOICES = {
        "ACTION": "Action",
        "DOCUMENTARY": "Documentary",
        "ROMANTIC": "Romantic",
        "DRAMA": "Drama",
    }

    RATING_CHOICES = [
    (0, "0"),
    (6, "6"),
    (12, "12"),
    (16, "16"),
    (18, "18"),
]

    title = models.CharField(max_length=30)
    description = models.TextField(max_length=500)
    genre = models.CharField(max_length=30, choices=GENRE_CHOICES, default="NEW")
    rating = models.IntegerField(choices=RATING_CHOICES, default=12, verbose_name="Rating (FSK)")
    ranking = models.DecimalField(decimal_places=1, max_digits=2,validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], default=0.0)
    duration = models.FloatField(default=0.0)
    image_file = models.FileField(upload_to='uploads/thumbnails/', null=True, blank=True)
    video_file = models.FileField(upload_to='uploads/videos/', null=True, blank=True)
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
    time = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

class ConnectionTestFile(models.Model):
    file = models.FileField(upload_to='uploads/testfile/', null=True, blank=True)