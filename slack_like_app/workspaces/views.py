from workspaces.models import Workspace, Channel
from django.contrib.auth.models import User
from workspaces.forms import CreateWorkspaceForm, CreateChannelForm
from django.views import View
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin


from workspaces.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView

class UserChatView(OwnerListView):
    model = User
    template_name = "workspaces/user_chat.html"

    def get(self, request, pk=None) :
        workspace = get_object_or_404(Workspace, id=pk)
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


class ChannelListView(OwnerListView):
    model = Channel
    template_name = "workspaces/channel_list.html"

    def get(self, request, pk=None) :
        workspace = get_object_or_404(Workspace, id=pk)
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

class ChannelDeleteView(generic.DeleteView):
    model = Channel
    template_name = "workspaces/channel_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        workspace = self.object.workspace
        return reverse('workspaces:channel_all', args=[workspace.id])

    def get(self, request, pk=None) :
        channel = get_object_or_404(Channel, id=pk)
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
        channel = get_object_or_404(Channel, id=pk)
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
        channel = get_object_or_404(Channel, id=pk)
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
        workspace = get_object_or_404(Workspace, channel=channel)
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
        workspace = get_object_or_404(Workspace, channel=channel)
        success_url = reverse('workspaces:channel_all', args=[workspace.id])
        channel.users.add(request.user)
        channel.save()
        return redirect(success_url)

class ChannelUpdateView(LoginRequiredMixin, View):
    template = 'workspaces/channel_update.html'

    def get(self, request, pk=None):
        channel = get_object_or_404(Channel, id=pk)
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
        channel = get_object_or_404(Channel, id=pk)
        form = CreateChannelForm(request.POST, request.FILES or None, instance=channel)

        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template, ctx)

        channel = form.save(commit=False)
        channel.save()

        workspace = get_object_or_404(Workspace, channel=channel)
        success_url = reverse('workspaces:channel_all', args=[workspace.id])

        return redirect(success_url)


class WorkspaceListView(OwnerListView):
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
        workspace = get_object_or_404(Workspace, id=pk)
        ctx = {'workspace_list' : workspace_list, "workspace" : workspace}
        return render(request, self.template, ctx)

    def post(self, request, pk=None) :
        workspace = get_object_or_404(Workspace, id=pk)
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
