from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Test(models.Model):
    title = models.CharField(max_length=120)
    content = models.TextField()
    image = models.ImageField(upload_to='media', null=True)

    def __str__(self):
        return self.title


class Userss(models.Model):
    user_id = models.CharField(max_length=20, primary_key=True, null=False)
    email_id = models.EmailField(max_length=70, null=True, unique=True)
    first_name = models.CharField(max_length=20, null=False)
    last_name = models.CharField(max_length=20, null=False)
    django_user = models.OneToOneField(User, related_name='django_user', on_delete=models.CASCADE, null=True)
    banner_image_url = models.CharField(max_length=500, default='http://127.0.0.1:8000/media/default_banner.jpg', null=True)
    profile_pic_url = models.CharField(max_length=500, default='http://127.0.0.1:8000/media/default-profile-picture.jpg', null=True)
    channel_name = models.CharField(max_length=50, null=True)


class Videos(models.Model):
    video_id = models.CharField(max_length=11, primary_key=True)
    user_id = models.ForeignKey(Userss, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=False)
    video_url = models.CharField(max_length=2048, null=False, unique=True)
    description = models.CharField(max_length=500, null=True)
    thumbnail = models.CharField(max_length=2048, null=False)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    release_date = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)


class Comments(models.Model):
    comment_id = models.CharField(max_length=20, primary_key=True)
    video_id = models.ForeignKey(Videos, on_delete=models.CASCADE)
    user_id = models.ForeignKey(Userss, on_delete=models.CASCADE)
    comment_date = models.DateTimeField(auto_now_add=True)
    comment_content = models.CharField(max_length=500, null=False)
    likes = models.IntegerField(default=0)


class WatchHistory(models.Model):
    user_id = models.ForeignKey(Userss, on_delete=models.CASCADE)
    video_id = models.ForeignKey(Videos, on_delete=models.CASCADE)
    watch_date = models.DateTimeField(auto_now_add=True)