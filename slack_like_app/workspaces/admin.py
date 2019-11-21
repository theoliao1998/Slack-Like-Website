from django.contrib import admin
from workspaces.models import Workspace, Channel, DateMessages, ChannelMessage, Reply, DirectMessage


# Register your models here.

admin.site.register(Workspace)
admin.site.register(Channel)
admin.site.register(DateMessages)
admin.site.register(ChannelMessage)
admin.site.register(Reply)
admin.site.register(DirectMessage)