from django.conf.urls import url
import src.views as views

app_name = 'src'
urlpatterns = [

    url(r'^login/$', views.Login.as_view(), name='login'),

    url(r'^logout/$', views.Logout, name='logout'),

    url(r'^registration/$', views.Registration.as_view(), name='registration'),

    url(r'^user/change_password/$', views.PasswordChange.as_view(), name='password_change'),

    url(r'^tasks/create/$', views.selector, {
        'GET': views.get_task_create,
        'POST': views.post_task_create
    }, name='task_create'),

    url(r'^tasks/delete/$', views.task_delete, name='task_delete'),

    url(r'^tasks/all/$', views.task_list, name='task_list'),

    url(r'^tasks/(?P<value>[0-9]+)/edit/$', views.selector, {
        'GET': views.get_task_edit,
        'POST': views.post_task_edit
    }, name='task_edit'),

    url(r'^roadmaps/create/$', views.selector, {
        'GET': views.get_roadmap_create,
        'POST': views.post_roadmap_create
    }, name='roadmap_create'),

    url(r'^roadmaps/delete/$', views.roadmap_delete, name='roadmap_delete'),

    url(r'^roadmaps/all/$', views.roadmap_list, name='roadmap_list'),

    url(r'^roadmaps/(?P<value>[0-9]+)/tasks/$', views.roadmap_tasks, name='roadmap_tasks'),

    url(r'^roadmaps/(?P<value>[0-9]+)/statistics/$', views.roadmap_statistics, name='roadmap_statistics'),

    url(r'^$', views.main, name='main'),

    url(r'^generate/$', views.generate_tasks, name='generate'),

]
