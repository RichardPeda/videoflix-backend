from django.db import models
from django.utils.timezone import now
from django.core.validators import MinValueValidator, MaxValueValidator

from userprofile.models import CustomUser

class Movie(models.Model):
    """
    Defines the Movie model, representing a film entry in the database.

    This model includes metadata and media associated with a movie, such as
    title, description, genre, age rating, user ranking, duration, and media files.

    Key features:
    - Provides predefined genre and rating choices for consistent data entry.
    - Supports upload of both image and video files.
    - Includes validation for ranking values (0.0-5.0).
    - Automatically tracks the creation timestamp.

    Fields:
    - title (CharField): The movie title (max 30 characters).
    - description (TextField): A short description of the movie (max 500 characters).
    - genre (CharField): The genre of the movie, selected from predefined choices (e.g., Action, Documentary).
    - rating (IntegerField): The age rating (FSK), selected from predefined integer choices (e.g., 6, 12, 16).
    - ranking (DecimalField): A user-defined ranking between 0.0 and 5.0 (1 decimal place).
    - duration (FloatField): Duration of the movie in minutes (default: 0.0).
    - image_file (FileField): Optional file field for the movies thumbnail image.
    - video_file (FileField): Optional file field for the movies video content.
    - created_at (DateTimeField): Timestamp automatically set at creation time.

    Methods:
    - __str__(): Returns a readable string representation of the movie using its ID and title.
    """
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
    """
    Defines the MovieConvertables model, which stores multiple video resolution versions
    associated with a specific Movie instance.

    This model is designed to hold transcoded versions of a movie's video file at
    different resolutions, allowing adaptive playback or quality selection.

    Fields:
    - movie (ForeignKey): A reference to the related Movie object. When the Movie is deleted,
    all associated MovieConvertables entries are also deleted (`on_delete=models.CASCADE`).
    The related name `movie_convertables` allows reverse access from Movie instances.

    - video_120p (FileField): Optional file field for the 120p resolution video version.
    - video_360p (FileField): Optional file field for the 360p resolution video version.
    - video_720p (FileField): Optional file field for the 720p resolution video version.
    - video_1080p (FileField): Optional file field for the 1080p resolution video version.

    Notes:
    - All video fields are optional (`null=True, blank=True`) to support partial conversions.
    - Files are stored in the 'uploads/videos/' directory.
    """
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_convertables')
    video_120p = models.FileField(upload_to='uploads/videos/', null=True, blank=True)
    video_360p = models.FileField(upload_to='uploads/videos/', null=True, blank=True)
    video_720p = models.FileField(upload_to='uploads/videos/', null=True, blank=True)
    video_1080p = models.FileField(upload_to='uploads/videos/', null=True, blank=True)

class MovieProgress(models.Model):
    """
    Defines the MovieProgress model, which tracks a user's viewing progress on a specific movie.

    This model records the timestamp (in seconds or minutes) at which a user paused or stopped watching,
    allowing for resume functionality or progress analytics.

    Fields:
    - movie (ForeignKey): References the related Movie. When the Movie is deleted,
    all related MovieProgress entries are also deleted. The `related_name='movie_progress'`
    allows reverse access from the Movie instance.

    - user (ForeignKey): References the user (via CustomUser) who is watching the movie.
    When the user is deleted, their progress entries are removed as well.

    - time (DecimalField): Stores the playback position (e.g., in seconds or minutes),
    allowing high precision with up to 20 digits and 2 decimal places. Nullable.

    - created_at (DateTimeField): Automatically set when the progress entry is first created.
    Not editable in the admin interface.

    - updated_at (DateTimeField): Automatically updated whenever the entry is saved.
    Not editable in the admin interface.

    Notes:
    - This model enables user-specific progress tracking per movie.
    - Suitable for implementing "Continue Watching" features or playback resumption.
    """
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_progress')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    time = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

class ConnectionTestFile(models.Model):
    """
    Defines the ConnectionTestFile model, used for uploading and storing test files.

    This model is typically used for connection checks, file upload testing, or validation
    of file handling functionality in the application.

    Fields:
    - file (FileField): An optional file field where test files can be uploaded.
    Files are saved in the 'uploads/testfile/' directory.
    The field allows null values and can be left blank.
    """
    file = models.FileField(upload_to='uploads/testfile/', null=True, blank=True)