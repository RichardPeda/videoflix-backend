import json
from .models import Movie, MovieConvertables
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
import subprocess
import os
from celery import shared_task
from django.core.files.base import ContentFile
from django.conf import settings



@receiver(post_save, sender=Movie)
def movie_post_save(sender, instance, created, **kwargs):
    """
    Signal handler triggered after a Movie instance is saved.

    Behavior:
    - If a new Movie instance is created and has a video file, triggers the `process_video` function.
    - If an existing Movie instance is updated and its `video_url` has changed to a new file,
      also triggers the `process_video` function.
    - Prevents re-processing if the video file remains unchanged.

    Parameters:
        sender (Model class): The model class that sent the signal (Movie).
        instance (Movie): The actual instance being saved.
        created (bool): True if a new record was created.
        **kwargs: Additional keyword arguments (not used here).

    Use case:
    This ensures that video processing (conversion, thumbnail generation) happens automatically
    on creation or whenever the video file is changed.
    """    
    if created and instance.video_url:
        process_video(instance)

    elif not created:
        try:
            previous = Movie.objects.get(pk=instance.pk)
        except Movie.DoesNotExist:
            previous = None

        if previous and previous.video_url != instance.video_url and instance.video_url:
            process_video(instance)

def process_video(instance: Movie):
    """
    Processes a Movie instance by extracting video metadata and queuing multiple
    asynchronous tasks to convert the video into various resolutions and generate a thumbnail.

    Workflow:
    - Retrieves the video's duration using the `get_duration` function and updates the Movie instance.
    - Ensures that a related MovieConvertables object exists for storing converted video file paths.
    - Dispatches Celery tasks to convert the video into multiple resolutions (120p, 360p, 720p, 1080p).
    - Dispatches a Celery task to generate a WebP thumbnail from the video.

    Parameters:
        instance (Movie): The Movie model instance representing the uploaded video.

    Notes:
        - All conversion and thumbnail generation tasks are executed asynchronously using Celery.
        - The function updates the `duration` field directly in the database to avoid unnecessary model reload.

    Example usage:
        process_video(movie_instance)
    """
    duration = get_duration(instance.video_url)
    Movie.objects.filter(pk=instance.pk).update(duration=duration)

    convertables, _ = MovieConvertables.objects.get_or_create(movie=instance)

    convert120p.delay(instance.video_url.path, convertables.id)
    convert360p.delay(instance.video_url.path, convertables.id)
    convert720p.delay(instance.video_url.path, convertables.id)
    convert1080p.delay(instance.video_url.path, convertables.id)
    generate_thumbnail.delay(instance.video_url.path, instance.pk)

     
def check_convert_status(status, file):
    if type(status) is bool:
            print(f'file {file} already exists')
            return None
    else:
        if status == 0:
            print(f'file {file} successfully created')
            return file
        else:
            print(f'error convert and create file {file}')
            return None
    
def get_duration(input_video):
    """
    Retrieves the duration of a video file using ffprobe.
    This function executes ffprobe to extract metadata about the first video stream
    of the given video file and returns the duration in seconds as a string.

    Parameters:
        input_video: A Django FileField or any object with a `.path` attribute pointing to the video file.

    Returns:
        duration (str): The duration of the video in seconds, as reported by ffprobe.

    Raises:
        subprocess.CalledProcessError: If ffprobe fails to execute.
        KeyError / IndexError: If the expected data is not found in the ffprobe output.
        json.JSONDecodeError: If the ffprobe output is not valid JSON.

    """
    result = subprocess.check_output(f'ffprobe -v quiet -show_streams -select_streams v:0 -of json "{input_video.path}"', shell=True).decode()
    fields = json.loads(result)['streams'][0]
    duration = fields['duration']
    return duration

@shared_task
def convert120p(file_path, convertables_id):
    """
    Converts a given video file to a low-resolution 120p MP4 format using FFmpeg,
    saves the converted file locally, and updates the corresponding MovieConvertables instance.

    The conversion parameters:
    - Resolution: 128x96 pixels
    - Video codec: libx264
    - Audio codec: aac
    - CRF (quality): 23 (default, reasonable quality)
    - Output format: MP4

    If the output file already exists, the conversion is skipped.

    Parameters:
        file_path (str): Absolute path to the original video file.
        convertables_id (int): Primary key of the MovieConvertables instance to update.

    Behavior:
        - Generates a new filename by appending '_120p.mp4' before the original file extension.
        - Runs FFmpeg as a subprocess with the specified encoding options.
        - Updates the 'video_120p' field of the MovieConvertables model with the new file path.
        - If the MovieConvertables instance does not exist, the function fails silently.
    """
    new_file_name = (file_path).split('.')
    new_file_name = new_file_name[0] + '_120p.mp4'

    if not os.path.exists(new_file_name):
        cmd = 'ffmpeg -i "{}" -s 128x96 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(file_path, new_file_name)
        subprocess.run(cmd, capture_output=True, shell=True)
    try:
        convertable = MovieConvertables.objects.get(pk=convertables_id)
        relative_path = os.path.relpath(new_file_name, settings.MEDIA_ROOT)
        convertable.video_120p = relative_path
        convertable.save()
    except MovieConvertables.DoesNotExist:
        pass
  
@shared_task
def convert360p(file_path, convertables_id):
    """
    Converts a given video file to a mid-resolution 360p MP4 format using FFmpeg,
    saves the converted file locally, and updates the corresponding MovieConvertables instance.

    The conversion parameters:
    - Resolution: 640x360 pixels
    - Video codec: libx264
    - Audio codec: aac
    - CRF (quality): 23 (default, reasonable quality)
    - Output format: MP4

    If the output file already exists, the conversion is skipped.

    Parameters:
        file_path (str): Absolute path to the original video file.
        convertables_id (int): Primary key of the MovieConvertables instance to update.

    Behavior:
        - Generates a new filename by appending '_360p.mp4' before the original file extension.
        - Runs FFmpeg as a subprocess with the specified encoding options.
        - Updates the 'video_360p' field of the MovieConvertables model with the new file path.
        - If the MovieConvertables instance does not exist, the function fails silently.
    """
    new_file_name = (file_path).split('.')
    new_file_name = new_file_name[0] + '_360p.mp4'

    if not os.path.exists(new_file_name):
        cmd = 'ffmpeg -i "{}" -s 640x360 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(file_path, new_file_name)

        subprocess.run(cmd, capture_output=True, shell=True)
    try:
        convertable = MovieConvertables.objects.get(pk=convertables_id)
        relative_path = os.path.relpath(new_file_name, settings.MEDIA_ROOT)
        convertable.video_360p = relative_path
        convertable.save()
    except MovieConvertables.DoesNotExist:
        pass

@shared_task
def convert720p(file_path, convertables_id):
    """
    Converts the given video file to 720p HD MP4 format using FFmpeg, saves the output,
    and updates the corresponding MovieConvertables instance with the new file path.

    Conversion details:
    - Resolution: 1280x720 (hd720)
    - Video codec: libx264
    - Audio codec: aac
    - CRF (quality): 23 (balanced quality)
    - Output format: MP4

    The function checks if the converted file already exists; if so, conversion is skipped.

    Parameters:
        file_path (str): Absolute path to the source video file.
        convertables_id (int): Primary key of the MovieConvertables object to update.

    Behavior:
        - Constructs the output filename by appending '_720p.mp4' before the file extension.
        - Executes FFmpeg command as a shell subprocess.
        - Updates the 'video_720p' field of the MovieConvertables model instance.
        - Silently ignores if the MovieConvertables instance does not exist.
    """
    new_file_name = (file_path).split('.')
    new_file_name = new_file_name[0] + '_720p.mp4'

    if not os.path.exists(new_file_name):
        cmd = 'ffmpeg -i "{}" -s hd720 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(file_path, new_file_name)
        subprocess.run(cmd, capture_output=True, shell=True)
    try:
        convertable = MovieConvertables.objects.get(pk=convertables_id)
        relative_path = os.path.relpath(new_file_name, settings.MEDIA_ROOT)
        convertable.video_720p = relative_path
        convertable.save()
    except MovieConvertables.DoesNotExist:
        pass

@shared_task
def convert1080p(file_path, convertables_id):
    """
    Converts the given video file to 1080p Full HD MP4 format using FFmpeg, saves the resulting file,
    and updates the associated MovieConvertables instance with the new file path.

    Conversion details:
    - Resolution: 1920x1080 (hd1080)
    - Video codec: libx264
    - Audio codec: aac
    - CRF (quality): 23 (balanced quality)
    - Output format: MP4

    If the output file already exists, the conversion process is skipped.

    Parameters:
        file_path (str): Absolute path to the original video file.
        convertables_id (int): Primary key of the MovieConvertables object to update.

    Behavior:
        - Constructs the new filename by appending '_1080p.mp4' before the file extension.
        - Executes FFmpeg as a shell subprocess to perform the conversion.
        - Updates the 'video_1080p' field of the MovieConvertables model.
        - Silently ignores the operation if the MovieConvertables instance does not exist.
    """
    new_file_name = (file_path).split('.')
    new_file_name = new_file_name[0] + '_1080p.mp4'

    if not os.path.exists(new_file_name):
        cmd = 'ffmpeg -i "{}" -s hd1080 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(file_path, new_file_name)
        subprocess.run(cmd, capture_output=True, shell=True)
    try:
        convertable = MovieConvertables.objects.get(pk=convertables_id)
        relative_path = os.path.relpath(new_file_name, settings.MEDIA_ROOT)
        convertable.video_1080p = relative_path
        convertable.save()
    except MovieConvertables.DoesNotExist:
        pass

@shared_task
def generate_thumbnail(video_path, instance_id):
    """
    Generates a WebP thumbnail from a video file using FFmpeg and saves it to the `image_url`
    field of the corresponding Movie model instance.

    This task performs the following steps:
    - Extracts a single frame from the video at the 1-second mark.
    - Converts the frame to the WebP image format using FFmpeg.
    - Passes the generated image directly to Django's FileField via an in-memory ContentFile.
    - Ensures the thumbnail is stored using the path defined in the model's `upload_to` attribute.

    Parameters:
        video_path (str): Absolute filesystem path to the input video file.
        instance_id (int): Primary key of the Movie instance to update.

    Notes:
        - This function avoids manually writing the image to disk to prevent duplicate storage.
        - The image is written directly to memory and saved via Djangos storage system.

    Exceptions:
        - subprocess.CalledProcessError: Raised if FFmpeg fails to generate the thumbnail.
        - Movie.DoesNotExist: Raised if the Movie instance no longer exists.
    """
    instance = Movie.objects.get(pk=instance_id)
    filename_base = os.path.splitext(os.path.basename(video_path))[0]
    thumb_filename = f"{filename_base}_thumb.webp"

    command = [
        'ffmpeg',
        '-i', video_path,
        '-ss', '00:00:01.000',
        '-vframes', '1',
        '-frames:v', '1',
        '-f', 'image2',
        '-vcodec', 'libwebp',
        'pipe:1'
    ]

    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        image_data = result.stdout
        content_file = ContentFile(image_data)
        instance.image_url.save(thumb_filename, content_file, save=True)

    except subprocess.CalledProcessError as e:
        print("FFmpeg error:", e.stderr.decode())