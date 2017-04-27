from django.conf.urls import url
from . import views

app_name = 'src'
urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^tasks/create/$', views.task_create, name='task_create'),
    url(r'^tasks/([0-9]+)/edit/$', views.task_edit, name='task_edit'),
    url(r'^tasks/all/$', views.task_list, name='task_list'),
    url(r'^tasks/([0-9]+)/delete', views.task_delete, name='task_delete'),
    url(r'^roadmaps/create/$', views.roadmap_create, name='roadmap_create'),
    url(r'^roadmaps/all/$', views.roadmap_list, name='roadmap_list'),
    url(r'^roadmaps/([0-9]+)/tasks/$', views.roadmap_tasks, name='roadmap_tasks'),
    url(r'^roadmaps/([0-9]+)/delete/$', views.roadmap_delete, name='roadmap_delete'),
    url(r'^roadmaps/([0-9]+)/statistics/$', views.roadmap_statistics, name='roadmap_statistics')
]
