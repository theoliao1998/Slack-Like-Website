from workspaces.models import Workspace, Channel, DirectMessage, Profile, DateMessages, ChannelMessage, Reply, Sharelink
from django.contrib.auth.models import User
from workspaces.forms import CreateWorkspaceForm, CreateChannelForm, CreateUserForm, DirectMessageForm, ChannelMessageForm, ProfileForm, ReplyForm
from django.views import View
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse
from django.contrib.humanize.templatetags.humanize import naturaltime, naturalday
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.http import HttpResponseNotFound
import datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required


from workspaces.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView

@receiver(user_logged_in)
def got_online(sender, user, request, **kwargs):
    if Profile.objects.filter(user=user):
        user.profile.is_online = True
        user.profile.save()
    else:
        Profile.objects.create(user=user,is_online=True)

@receiver(user_logged_out)
def got_offline(sender, user, request, **kwargs):
    if Profile.objects.filter(user=user):
        user.profile.is_online = False
        user.profile.save()
    else:
        Profile.objects.create(user=user)

class ChannelView(LoginRequiredMixin, View):
    model = Channel
    template_name = "workspaces/channel_messages.html"

    def get(self, request, pk=None):
        channel = get_object_or_404(Channel, id=pk, users=request.user)
        workspace = channel.workspace
        channel_list_belong = workspace.channel_set.filter(users__username=request.user)
        members = channel.users.all()
        datemessages = reversed(list(DateMessages.objects.filter(channel=channel).order_by('-date')[:7]))
        more = False
        if members.count() > 6:
            members = members[:6]
            more = True
        #reply_form = ReplyForm()
        ctx = {'channel_list_belong' : channel_list_belong, 'channel':channel, 'workspace': workspace, 'members':members,'more':more, 'datemessages':datemessages}
        return render(request, self.template_name, ctx)


class ChannelMessageCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        channel = get_object_or_404(Channel, id=pk, users=request.user)
        msg_form = ChannelMessageForm(request.POST)
        date_msgs,_ = DateMessages.objects.get_or_create(channel=channel, date=datetime.date.today())
        msg = ChannelMessage(content=request.POST.get('content'), user=request.user, date=date_msgs)
        msg.save()
        return HttpResponse()

class ReplyCreateView(LoginRequiredMixin, View):
    def post(self, request, pk=None):
        msg = get_object_or_404(ChannelMessage, id=pk)
        reply = Reply(content=request.POST.get('content'), user=request.user, channel_message=msg)
        reply.save()
        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class ChannelMessageDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        msg = get_object_or_404(ChannelMessage, id=pk, user=request.user)
        date_msgs = msg.date
        if date_msgs.channelmessage_set.count() == 1:
            try:
                date_msgs.delete()
            except DateMessages.DoesNotExist as e:
                pass
        else:
            try:
                msg.delete()
            except ChannelMessage.DoesNotExist as e:
                pass

        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class ReplyDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        reply = get_object_or_404(Reply, id=pk, user=request.user)

        try:
            reply.delete()
        except Reply.DoesNotExist as e:
            pass

        return HttpResponse()

class ChannelMessages(LoginRequiredMixin, View) :
    def get(self, request, pk=None):
        channel = Channel.objects.get(id=pk, users=request.user)
        datemessages = reversed(list(DateMessages.objects.filter(channel=channel).order_by('-date')[:7]))

        results = {}
        for d in datemessages:
            results[naturalday(d.date)] = []
            for message in d.channelmessage_set.all():
                repliers = set()
                cnt = message.reply_set.count()
                l = naturaltime(message.reply_set.order_by('-created_at')[0].created_at) if cnt else 0
                for reply in message.reply_set.all():
                    if reply.user.username not in repliers:
                        repliers.add(reply.user.username)

                results[naturalday(d.date)].append([message.user.username, naturaltime(message.created_at), message.content, message.user==request.user, message.id, message.user.id, list(repliers),cnt,l])

        return JsonResponse(results, safe=False)

class ReplyMessages(LoginRequiredMixin, View) :
    def get(self, request, pk=None):
        msg = ChannelMessage.objects.get(id=pk, date__channel__users=request.user)
        replies = msg.reply_set.all()
        results = []
        for reply in replies:
            result = [reply.user.username, naturaltime(reply.created_at), reply.content, reply.user==request.user, reply.id, reply.user.id]
            results.append(result)
        return JsonResponse(results, safe=False)

class UserMessages(LoginRequiredMixin, View) :
    def get(self, request, pk=None):
        selected_one = get_user_model().objects.get(id=pk)
        messages = reversed(list(DirectMessage.objects.filter(
            Q(user=request.user, receiver=selected_one) | Q(user=selected_one, receiver=request.user)
        ).order_by('-created_at')[:20]))
        results = []
        for message in messages:
            result = [message.user.username, naturaltime(message.created_at), message.content, message.user==request.user, message.id, message.user.id]
            results.append(result)
        return JsonResponse(results, safe=False)

class UserMessageCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        receiver = get_object_or_404(User, id=pk)
        msg_form = DirectMessageForm(request.POST)
        d_msg = DirectMessage(content=request.POST.get('content'), user=request.user, receiver=receiver)
        d_msg.save()
        return HttpResponse()

def createSharelink(workspace,user):
    try:
        sharelink = Sharelink.objects.create(owner=user,workspace=workspace,addr=User.objects.make_random_password(length=14))
        return sharelink
    except:
        return createSharelink(workspace)

@method_decorator(csrf_exempt, name='dispatch')
class SharelinkCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        workspace = get_object_or_404(Workspace, id=pk, users=request.user)
        sharelink = createSharelink(workspace,request.user)

        return redirect(reverse('workspaces:workspace_members', args=[pk]))

@method_decorator(csrf_exempt, name='dispatch')
class UserMessageDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        msg = get_object_or_404(DirectMessage, id=pk, user=request.user)
        try:
            msg.delete()
        except DirectMessage.DoesNotExist as e:
            pass

        return HttpResponse()


class UserChatView(LoginRequiredMixin,OwnerListView):
    model = User
    template_name = "workspaces/user_chat.html"

    def get(self, request, pk1=None, pk2=None) :
        workspace = get_object_or_404(Workspace, id=pk1, users=request.user)
        channel_list_belong = workspace.channel_set.filter(users__username=request.user)
        members = workspace.users
        selected_one = members.get(id=pk2)
        msgs = reversed(list(DirectMessage.objects.filter(
            Q(user=request.user, receiver=selected_one) | Q(user=selected_one, receiver=request.user)
        ).order_by('-created_at')[:20]))
        members=members.all()
        msg_form = DirectMessageForm()
        more = False
        if members.count() > 6:
            members = members[:6]
            more = True
        ctx = {'channel_list_belong' : channel_list_belong, 'workspace': workspace, 'selected_one':selected_one, 'members':members,'more':more, 'msgs':msgs, 'msg_form':msg_form}
        return render(request, self.template_name, ctx)

class UserUpdateView(LoginRequiredMixin, View):
    template_name = "workspaces/user_update.html"

    def get(self, request, pk1=None, pk2=None) :
        workspace = get_object_or_404(Workspace, id=pk1, users=request.user)
        channel_list_belong = workspace.channel_set.filter(users__username=request.user)
        members = workspace.users
        selected_one = members.get(id=pk2)
        profile = selected_one.profile
        msgs = reversed(list(DirectMessage.objects.filter(
            Q(user=request.user, receiver=selected_one) | Q(user=selected_one, receiver=request.user)
        ).order_by('-created_at')[:20]))
        msg_form = DirectMessageForm()
        form = CreateUserForm(instance=selected_one)
        form2 = ProfileForm(instance=profile)
        members=members.all()
        more = False
        if members.count() > 6:
            members = members[:6]
            more = True
        ctx = {'channel_list_belong' : channel_list_belong, 'workspace': workspace, 'selected_one':selected_one, 'members':members,'more':more, 'form':form, 'form2':form2, 'msgs':msgs,'msg_form':msg_form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk1=None, pk2=None) :
        user = get_object_or_404(User, id=pk2)
        profile = user.profile
        form = CreateUserForm(request.POST, request.FILES or None, instance=user)
        form2 = ProfileForm(request.POST, request.FILES or None, instance=profile)

        if (not form.is_valid()) or (not form2.is_valid()):
            workspace = get_object_or_404(Workspace, id=pk1, users=request.user)
            channel_list_belong = workspace.channel_set.filter(users__username=request.user)
            members = workspace.users
            selected_one = members.get(id=pk2)
            profile = selected_one.profile
            msgs = reversed(list(DirectMessage.objects.filter(
                Q(user=request.user, receiver=selected_one) | Q(user=selected_one, receiver=request.user)
            ).order_by('-created_at')[:20]))
            msg_form = DirectMessageForm()
            members=members.all()
            more = False
            if members.count() > 6:
                members = members[:6]
                more = True
            ctx = {'channel_list_belong' : channel_list_belong, 'workspace': workspace, 'selected_one':selected_one, 'members':members,'more':more, 'form':form, 'form2':form2, 'msgs':msgs,'msg_form':msg_form}
            return render(request, self.template_name, ctx)

        user = form.save(commit=False)
        user.save()
        profile = form2.save(commit=False)
        profile.save()

        success_url = reverse('workspaces:workspace_user', args=[pk1,pk2])

        return redirect(success_url)


class ChannelListView(LoginRequiredMixin,OwnerListView):
    model = Channel
    template_name = "workspaces/channel_list.html"

    def get(self, request, pk=None) :
        workspace = get_object_or_404(Workspace, id=pk, users=request.user)
        channel_list_belong = workspace.channel_set.filter(users__username=request.user)
        channel_list_other = workspace.channel_set.exclude(users__username=request.user)
        form = CreateChannelForm()
        members = workspace.users.all()
        more = False
        if members.count() > 6:
            members = members[:6]
            more = True
        ctx = {'channel_list_belong' : channel_list_belong, 'channel_list_other' : channel_list_other, 'workspace': workspace, 'form': form, 'members':members,'more':more}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None) :
        form = CreateChannelForm(request.POST, request.FILES or None)

        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        channel = form.save(commit=False)
        channel.workspace = Workspace.objects.get(id=pk)
        channel.save()
        channel.users.add(self.request.user)
        channel.save()
        return redirect(reverse('workspaces:channel_all', args=[pk]))

class ChannelDeleteView(LoginRequiredMixin,generic.DeleteView):
    model = Channel
    template_name = "workspaces/channel_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        workspace = self.object.workspace
        return reverse('workspaces:channel_all', args=[workspace.id])

    def get(self, request, pk=None) :
        channel = get_object_or_404(Channel, id=pk, workspace__owner=request.user)
        workspace = get_object_or_404(Workspace, channel=channel)
        channel_list_belong = workspace.channel_set.filter(users__username=request.user)
        channel_list_other = workspace.channel_set.exclude(users__username=request.user)
        members = workspace.users.all()
        more = False
        if members.count() > 6:
            members = members[:6]
            more = True
        ctx = {'channel_list_belong' : channel_list_belong, 'channel_list_other' : channel_list_other, 'channel': channel, 'workspace':workspace,'members':members,'more':more}
        return render(request, self.template_name, ctx)

class ChannelLeaveView(LoginRequiredMixin, View):
    template = 'workspaces/channel_leave.html'

    def get(self, request, pk=None) :
        channel = get_object_or_404(Channel, id=pk, users=request.user)
        workspace = get_object_or_404(Workspace, channel=channel)
        channel_list_belong = workspace.channel_set.filter(users__username=request.user)
        channel_list_other = workspace.channel_set.exclude(users__username=request.user)
        last_one = channel.users.all().count() == 1
        members = workspace.users.all()
        more = False
        if members.count() > 6:
            members = members[:6]
            more = True
        ctx = {'channel_list_belong' : channel_list_belong, 'channel_list_other' : channel_list_other, 'channel': channel, 'workspace':workspace, 'last_one':last_one, 'members':members,'more':more}
        return render(request, self.template, ctx)

    def post(self, request, pk=None) :
        channel = get_object_or_404(Channel, id=pk, users=request.user)
        workspace = get_object_or_404(Workspace, channel=channel)
        success_url = reverse('workspaces:channel_all', args=[workspace.id])
        channel.users.remove(request.user)
        channel.save()

        if channel.users.all().count() == 0:
            channel.delete()

        return redirect(success_url)

class ChannelJoinView(LoginRequiredMixin, View):
    template = 'workspaces/channel_join.html'

    def get(self, request, pk=None) :
        channel = get_object_or_404(Channel, id=pk)
        workspace = get_object_or_404(Workspace, channel=channel, users=request.user)
        channel_list_belong = workspace.channel_set.filter(users__username=request.user)
        channel_list_other = workspace.channel_set.exclude(users__username=request.user)
        members = workspace.users.all()
        more = False
        if members.count() > 6:
            members = members[:6]
            more = True
        ctx = {'channel_list_belong' : channel_list_belong, 'channel_list_other' : channel_list_other, 'channel': channel, 'workspace':workspace,'members':members,'more':more}
        return render(request, self.template, ctx)

    def post(self, request, pk=None) :
        channel = get_object_or_404(Channel, id=pk)
        workspace = get_object_or_404(Workspace, channel=channel, users=request.user)
        success_url = reverse('workspaces:channel_all', args=[workspace.id])
        channel.users.add(request.user)
        channel.save()
        return redirect(success_url)

class ChannelUpdateView(LoginRequiredMixin, View):
    template = 'workspaces/channel_update.html'

    def get(self, request, pk=None):
        channel = get_object_or_404(Channel, id=pk, users=request.user)
        workspace = get_object_or_404(Workspace, channel=channel)
        channel_list_belong = workspace.channel_set.filter(users__username=request.user)
        channel_list_other = workspace.channel_set.exclude(users__username=request.user)
        form = CreateChannelForm(instance=channel)
        members = workspace.users.all()
        more = False
        if members.count() > 6:
            members = members[:6]
            more = True
        ctx = {'channel_list_belong' : channel_list_belong, 'channel_list_other' : channel_list_other, 'channel': channel, 'workspace':workspace, 'form':form, 'members':members, 'more':more}
        return render(request, self.template, ctx)

    def post(self, request, pk=None) :
        channel = get_object_or_404(Channel, id=pk, users=request.user)
        form = CreateChannelForm(request.POST, request.FILES or None, instance=channel)

        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template, ctx)

        channel = form.save(commit=False)
        channel.save()

        workspace = get_object_or_404(Workspace, channel=channel)
        success_url = reverse('workspaces:channel_all', args=[workspace.id])

        return redirect(success_url)


class WorkspaceListView(LoginRequiredMixin,OwnerListView):
    model = Workspace
    template_name = "workspaces/home_list.html"

    def get(self, request) :
        workspace_list = Workspace.objects.filter(users__username=request.user)
        form = CreateWorkspaceForm()

        ctx = {'workspace_list' : workspace_list,'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None) :
        form = CreateWorkspaceForm(request.POST, request.FILES or None)

        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template, ctx)

        # Add owner to the model before saving
        workspace = form.save(commit=False)
        workspace.owner = self.request.user
        workspace.save()
        workspace.users.add(workspace.owner)
        workspace.save()
        return redirect(reverse_lazy('workspaces:all'))

class WorkspaceDeleteView(OwnerDeleteView):
    model = Workspace
    template_name = "workspaces/workspace_delete.html"

    def get(self, request, pk=None) :
        workspace_list = Workspace.objects.filter(users__username=request.user)
        workspace = self.get_object()
        ctx = {'workspace_list' : workspace_list, "workspace" : workspace}
        return render(request, self.template_name, ctx)

class WorkspaceLeaveView(LoginRequiredMixin, View):
    template = 'workspaces/workspace_leave.html'
    success_url = reverse_lazy('workspaces:all')

    def get(self, request, pk=None) :
        workspace_list = Workspace.objects.filter(users__username=request.user)
        workspace = get_object_or_404(Workspace, id=pk, users=request.user)
        ctx = {'workspace_list' : workspace_list, "workspace" : workspace}
        return render(request, self.template, ctx)

    def post(self, request, pk=None) :
        workspace = get_object_or_404(Workspace, id=pk, users=request.user)
        workspace.users.remove(request.user)
        workspace.save()

        return redirect(self.success_url)

class WorkspaceUpdateView(LoginRequiredMixin, View):
    template = 'workspaces/workspace_update.html'
    success_url = reverse_lazy('workspaces:all')
    def get(self, request, pk) :
        workspace_list = Workspace.objects.filter(users__username=request.user)
        workspace = get_object_or_404(Workspace, id=pk, owner=self.request.user)
        form = CreateWorkspaceForm(instance=workspace)
        ctx = {'workspace_list' : workspace_list,"workspace" : workspace, 'form': form }
        return render(request, self.template, ctx)

    def post(self, request, pk=None) :
        workspace = get_object_or_404(Workspace, id=pk, owner=self.request.user)
        form = CreateWorkspaceForm(request.POST, request.FILES or None, instance=workspace)

        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template, ctx)

        workspace = form.save(commit=False)
        workspace.save()

        return redirect(self.success_url)

class WorkspaceShareView(LoginRequiredMixin, View):
    template = 'workspaces/workspace_sharelink.html'

    def get(self, request, pk, addr=None) :
        workspace_list = Workspace.objects.filter(users__username=request.user)
        sharelink = get_object_or_404(Sharelink, addr=addr)
        if timezone.now() > sharelink.expired_at:
            return HttpResponseNotFound("hello")

        workspace = sharelink.workspace
        if workspace.id != pk:
            return HttpResponseNotFound("hello")

        ctx = {'workspace_list' : workspace_list,"workspace" : workspace}
        return render(request, self.template, ctx)

    def post(self, request, pk=None, addr=None) :
        sharelink = get_object_or_404(Sharelink, addr=addr)
        if timezone.now() > sharelink.expired_at:
            return HttpResponseNotFound("hello")

        workspace = sharelink.workspace
        if workspace.id != pk:
            return HttpResponseNotFound("hello")

        workspace.users.add(request.user)
        workspace.save()
        success_url = reverse('workspaces:channel_all', args=[pk])
        return redirect(success_url)

class WorkspaceMembersView(LoginRequiredMixin, View):
    template = 'workspaces/workspace_members.html'

    def get(self, request, pk) :
        workspace = get_object_or_404(Workspace, id=pk, users=request.user)
        sharelinks = workspace.sharelink_set.filter(expired_at__gte=datetime.datetime.now())
        channel_list_belong = workspace.channel_set.filter(users__username=request.user)
        members = workspace.users.all()
        more = False
        if members.count() > 6:
            members = members[:6]
            more = True
        ctx = {'channel_list_belong' : channel_list_belong,'workspace': workspace,'members':members,'more':more, 'sharelinks':sharelinks}
        return render(request, self.template, ctx)
