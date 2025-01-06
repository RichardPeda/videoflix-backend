import json
from .models import Movie, MovieConvertables
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.conf import settings
from django.core.mail import send_mail
import subprocess
from django.contrib.auth.models import User
import os


@receiver(post_save, sender=Movie)
def movie_post_save(sender, instance, created, **kwargs):
    if instance.video_url:  
        duration = get_duration(instance.video_url)
        Movie.objects.filter(pk=instance.pk).update(duration=duration)
        
        try:
            convertables = MovieConvertables.objects.get(movie=instance)
        except:
            convertables = MovieConvertables.objects.create(movie=instance)
        
        
        status, file = convert120p(instance.video_url)
        ret_val = check_convert_status(status=status, file=file)
        if ret_val is not None:
            convertables.video_120p = ret_val
            
        status, file = convert360p(instance.video_url)
        ret_val = check_convert_status(status=status, file=file)
        
        if ret_val is not None:
            convertables.video_360p = ret_val

        status, file = convert720p(instance.video_url)
        ret_val = check_convert_status(status=status, file=file)
        
        if ret_val is not None:
            convertables.video_720p = ret_val

        status, file = convert1080p(instance.video_url)
        ret_val = check_convert_status(status=status, file=file)
        
        if ret_val is not None:
            convertables.video_1080p = ret_val
        
        convertables.save()


        # send_email_to_user()
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
    if os.path.exists(new_file_name):
        return True, new_file_name
    else:
        cmd = 'ffmpeg -i "{}" -s 128x96 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source.path, new_file_name)
        run = subprocess.run(cmd, capture_output=True, shell=True)
        return run.returncode, new_file_name
    
    
def convert360p(source):
    new_file_name = (str(source.path)).split('.')
    new_file_name = new_file_name[0] + '_360p.mp4'
    if os.path.exists(new_file_name):
        return True, new_file_name
    else:
        cmd = 'ffmpeg -i "{}" -s 352x480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source.path, new_file_name)
        run = subprocess.run(cmd, capture_output=True, shell=True)
        return run.returncode, new_file_name

def convert720p(source):
    new_file_name = (str(source.path)).split('.')
    new_file_name = new_file_name[0] + '_720p.mp4'
    if os.path.exists(new_file_name):
        return True, new_file_name
    else:
        cmd = 'ffmpeg -i "{}" -s hd720 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source.path, new_file_name)
        run = subprocess.run(cmd, capture_output=True, shell=True)
        return run.returncode, new_file_name
       
def convert1080p(source):
    new_file_name = (str(source.path)).split('.')
    new_file_name = new_file_name[0] + '_1080p.mp4'
    if os.path.exists(new_file_name):
        return True, new_file_name
    else:
        cmd = 'ffmpeg -i "{}" -s hd1080 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source.path, new_file_name)
        run = subprocess.run(cmd, capture_output=True, shell=True)
        return run.returncode, new_file_name


# 120p, 360p, 720p, 1080p