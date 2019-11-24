from workspaces.models import Workspace
from workspaces.forms import CreateWorkspaceForm
from django.views import View
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin


from workspaces.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView

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

class WorkspaceDeleteView(generic.DeleteView):
    model = Workspace
    template_name = "workspaces/workspace_delete.html"

    def get(self, request, pk=None) :
        workspace_list = Workspace.objects.filter(users__username=request.user)
        workspace = self.get_object()
        ctx = {'workspace_list' : workspace_list, "workspace" : workspace}
        return render(request, self.template_name, ctx)

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
