from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import User
from django.conf import settings
from datetime import datetime, timedelta

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

    # Shows up in the list
    def __str__(self):
        return self.name

class Sharelink(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    expired_at = models.DateTimeField(default=datetime.now()+timedelta(days=30))
    addr = models.CharField(max_length=20)

    class Meta:
        unique_together = ('workspace', 'addr',)

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
    date = models.DateField(auto_now_add=True)

class ChannelMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.ForeignKey(DateMessages, on_delete=models.CASCADE)
    content = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_last_reply_time(self):
        try:
            return self.reply_set.all().order_by('-created_at')[0].created_at
        except IndexError:
            pass

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





