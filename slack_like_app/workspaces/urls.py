from django.urls import path, reverse_lazy
from . import views

app_name='workspaces'
urlpatterns = [
    path('', views.WorkspaceListView.as_view(), name='all'),
    path('workspace/<int:pk>/delete',
        views.WorkspaceDeleteView.as_view(success_url=reverse_lazy('workspaces:all')), name='workspace_delete'),
    path('ad/<int:pk>/update',
        views.WorkspaceUpdateView.as_view(success_url=reverse_lazy('workspaces:all')), name='workspace_update'),
]