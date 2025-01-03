import json
from .models import Movie
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.conf import settings
import subprocess


@receiver(post_save, sender=Movie)
def movie_post_save(sender, instance, created, **kwargs):
    if instance.video_url:  
        convert720p(instance.video_url)
        duration = get_duration(instance.video_url)
        Movie.objects.filter(pk=instance.pk).update(duration=duration)
    


def get_duration(input_video): 
    result = subprocess.check_output(f'ffprobe -v quiet -show_streams -select_streams v:0 -of json "{input_video.path}"', shell=True).decode()
    fields = json.loads(result)['streams'][0]
    duration = fields['duration']
    return duration
    
def convert720p(source):
    new_file_name = (str(source.path)).split('.')
    new_file_name = new_file_name[0] + '_720p.mp4'
    cmd = 'ffmpeg -i "{}" -s hd720 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source.path, new_file_name)
    print(cmd)
    run = subprocess.run(cmd, capture_output=True)
