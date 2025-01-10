import json
from .models import Movie, MovieConvertables
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.conf import settings
import subprocess
from django.contrib.auth.models import User
import os
from celery import shared_task


@receiver(post_save, sender=Movie)
def movie_post_save(sender, instance, created, **kwargs):
    if instance.video_url:  
        duration = get_duration(instance.video_url)
        Movie.objects.filter(pk=instance.pk).update(duration=duration)
        convertables, created = MovieConvertables.objects.get_or_create(movie=instance)
               
        convert120p.delay(instance.video_url.path, convertables.id)
       
        convert360p.delay(instance.video_url.path, convertables.id)
     
        convert720p.delay(instance.video_url.path, convertables.id)
       
        convert1080p.delay(instance.video_url.path, convertables.id)
     
        

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
    result = subprocess.check_output(f'ffprobe -v quiet -show_streams -select_streams v:0 -of json "{input_video.path}"', shell=True).decode()
    fields = json.loads(result)['streams'][0]
    duration = fields['duration']
    return duration

@shared_task
def convert120p(file_path, convertables_id):
    new_file_name = (file_path).split('.')
    new_file_name = new_file_name[0] + '_120p.mp4'

    if not os.path.exists(new_file_name):
        cmd = 'ffmpeg -i "{}" -s 128x96 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(file_path, new_file_name)
        subprocess.run(cmd, capture_output=True, shell=True)
    try:
        convertable = MovieConvertables.objects.get(pk=convertables_id)
        convertable.video_120p = new_file_name
        convertable.save()
    except MovieConvertables.DoesNotExist:
        pass
  
@shared_task
def convert360p(file_path, convertables_id):
    new_file_name = (file_path).split('.')
    new_file_name = new_file_name[0] + '_360p.mp4'

    if not os.path.exists(new_file_name):
        cmd = 'ffmpeg -i "{}" -s 352x480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(file_path, new_file_name)
        subprocess.run(cmd, capture_output=True, shell=True)
    try:
        convertable = MovieConvertables.objects.get(pk=convertables_id)
        convertable.video_360p = new_file_name
        convertable.save()
    except MovieConvertables.DoesNotExist:
        pass

@shared_task
def convert720p(file_path, convertables_id):
    new_file_name = (file_path).split('.')
    new_file_name = new_file_name[0] + '_720p.mp4'

    if not os.path.exists(new_file_name):
        cmd = 'ffmpeg -i "{}" -s hd720 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(file_path, new_file_name)
        subprocess.run(cmd, capture_output=True, shell=True)
    try:
        convertable = MovieConvertables.objects.get(pk=convertables_id)
        convertable.video_720p = new_file_name
        convertable.save()
    except MovieConvertables.DoesNotExist:
        pass

@shared_task
def convert1080p(file_path, convertables_id):
    new_file_name = (file_path).split('.')
    new_file_name = new_file_name[0] + '_1080p.mp4'

    if not os.path.exists(new_file_name):
        cmd = 'ffmpeg -i "{}" -s hd1080 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(file_path, new_file_name)
        subprocess.run(cmd, capture_output=True, shell=True)
    try:
        convertable = MovieConvertables.objects.get(pk=convertables_id)
        convertable.video_1080p = new_file_name
        convertable.save()
    except MovieConvertables.DoesNotExist:
        pass