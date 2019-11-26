from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import User
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)
    content = models.CharField(max_length=255, blank=True, null=True)

class Workspace(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    users = models.ManyToManyField(User,related_name='auth_users_of_workspace')
    name = models.CharField(max_length=255,
        validators=[MinLengthValidator(2, "Name must be greater than 2 characters")])
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sharelink = models.CharField(max_length=20,default=User.objects.make_random_password(length=14))

    # Shows up in the list
    def __str__(self):
        return self.name

class Channel(models.Model):
    users = models.ManyToManyField(User,related_name='auth_users_of_channel')
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    name = models.CharField(max_length=255,
        validators=[MinLengthValidator(2, "Name must be greater than 2 characters")])
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Shows up in the list
    def __str__(self):
        return self.name

class DateMessages(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, default=1)
    created_at = models.DateTimeField(auto_now_add=True)

class ChannelMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.ForeignKey(DateMessages, on_delete=models.CASCADE)
    content = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Reply(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    channel_message = models.ForeignKey(ChannelMessage, on_delete=models.CASCADE)
    content = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class DirectMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User,related_name='receiver', on_delete=models.CASCADE)
    content = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)





