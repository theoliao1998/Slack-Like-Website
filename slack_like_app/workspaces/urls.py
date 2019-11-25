from django.urls import path, reverse_lazy
from . import views

app_name='workspaces'
urlpatterns = [
    path('', views.WorkspaceListView.as_view(), name='all'),
    path('workspace/<int:pk>/delete',
        views.WorkspaceDeleteView.as_view(success_url=reverse_lazy('workspaces:all')), name='workspace_delete'),
    path('workspace/<int:pk>/leave',
        views.WorkspaceLeaveView.as_view(success_url=reverse_lazy('workspaces:all')), name='workspace_leave'),
    path('workspace/<int:pk>/update',
        views.WorkspaceUpdateView.as_view(success_url=reverse_lazy('workspaces:all')), name='workspace_update'),
    path('workspace/<int:pk>',
        views.ChannelListView.as_view(), name='channel_all'),
    path('channel/<int:pk>/delete',
        views.ChannelDeleteView.as_view(success_url=reverse_lazy('workspaces')), name='channel_delete'),
    path('channel/<int:pk>/leave',
        views.ChannelLeaveView.as_view(), name='channel_leave'),
    path('channel/<int:pk>/join',
        views.ChannelJoinView.as_view(), name='channel_join'),
    path('channel/<int:pk>/update',
        views.ChannelUpdateView.as_view(), name='channel_update'),

]