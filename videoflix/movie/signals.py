import json
from .models import Movie
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.conf import settings
from django.core.mail import send_mail
import subprocess
from django.contrib.auth.models import User


@receiver(post_save, sender=Movie)
def movie_post_save(sender, instance, created, **kwargs):
    if instance.video_url:  
        duration = get_duration(instance.video_url)
        Movie.objects.filter(pk=instance.pk).update(duration=duration)
        # convert120p(instance.video_url)
        # convert360p(instance.video_url)
        # convert720p(instance.video_url)
        # convert1080p(instance.video_url)
        send_email_to_user()
        
    
def send_email_to_user():
    sender = settings.EMAIL_FROM
    user = User.objects.get(username='richard')
    send_mail(
        subject= "Registrierung abschließen",
        message= f"Hello {user.username}, bitte klicke auf den link",
        from_email= sender,
        recipient_list= [user.email],
        fail_silently=False,
        )
    

def get_duration(input_video): 
    result = subprocess.check_output(f'ffprobe -v quiet -show_streams -select_streams v:0 -of json "{input_video.path}"', shell=True).decode()
    fields = json.loads(result)['streams'][0]
    duration = fields['duration']
    return duration

def convert120p(source):
    new_file_name = (str(source.path)).split('.')
    new_file_name = new_file_name[0] + '_120p.mp4'
    cmd = 'ffmpeg -i "{}" -s 128x96 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source.path, new_file_name)
    subprocess.run(cmd, capture_output=True, shell=True)
    
def convert360p(source):
    new_file_name = (str(source.path)).split('.')
    new_file_name = new_file_name[0] + '_360p.mp4'
    cmd = 'ffmpeg -i "{}" -s 352x480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source.path, new_file_name)
    subprocess.run(cmd, capture_output=True, shell=True)

def convert720p(source):
    new_file_name = (str(source.path)).split('.')
    new_file_name = new_file_name[0] + '_720p.mp4'
    cmd = 'ffmpeg -i "{}" -s hd720 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source.path, new_file_name)
    subprocess.run(cmd, capture_output=True, shell=True)
    
def convert1080p(source):
    new_file_name = (str(source.path)).split('.')
    new_file_name = new_file_name[0] + '_1080p.mp4'
    cmd = 'ffmpeg -i "{}" -s hd1080 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source.path, new_file_name)
    subprocess.run(cmd, capture_output=True, shell=True)


# 120p, 360p, 720p, 1080p