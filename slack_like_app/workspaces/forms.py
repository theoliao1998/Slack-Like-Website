from django import forms
from workspaces.models import Workspace, Channel
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from workspaces.humanize import naturalsize
from django.core.exceptions import ValidationError
from django.core import validators

# https://docs.djangoproject.com/en/2.1/topics/http/file-uploads/
# https://stackoverflow.com/questions/2472422/django-file-upload-size-limit
# https://stackoverflow.com/questions/32007311/how-to-change-data-in-django-modelform
# https://docs.djangoproject.com/en/2.1/ref/forms/validation/#cleaning-and-validating-fields-that-depend-on-each-other

# Create the form class.

class CreateWorkspaceForm(forms.ModelForm):
    max_upload_limit = 2 * 1024 * 1024
    max_upload_limit_text = naturalsize(max_upload_limit)

    class Meta:
        model = Workspace
        fields = ['name','description']

class CreateChannelForm(forms.ModelForm):
    max_upload_limit = 2 * 1024 * 1024
    max_upload_limit_text = naturalsize(max_upload_limit)

    class Meta:
        model = Channel
        fields = ['name','description']


class CreateUserForm(forms.ModelForm):
    max_upload_limit = 2 * 1024 * 1024
    max_upload_limit_text = naturalsize(max_upload_limit)

    class Meta:
        model = User
        fields = ['username','first_name','last_name','email']

class DirectMessageForm(forms.Form):
    content = forms.CharField(required=True, max_length=255, strip=True)
