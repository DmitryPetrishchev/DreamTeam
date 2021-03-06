from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
import src.views as views

app_name = 'src'
urlpatterns = [

    url(r'^login/$', views.Login.as_view(), name='login'),

    url(r'^logout/$', views.Logout, name='logout'),

    url(r'^registration/$', views.Registration.as_view(), name='registration'),

    url(r'^user/profile/$', views.user_profile, name='user_profile'),

    url(r'^user/change_profile/$', views.UserChange.as_view(), name='user_change'),

    url(r'^user/change_profile/upload_image/$', views.image_upload, name='image_upload'),

    url(r'^user/change_profile/delete_image/$', views.image_delete, name='image_delete'),

    url(r'^user/change_password/$', views.PasswordChange.as_view(), name='password_change'),

    url(r'^tasks/create/$', views.TaskCreate.as_view(), name='task_create'),

    url(r'^tasks/delete/$', views.task_delete, name='task_delete'),

    url(r'^tasks/all/$', views.task_list, name='task_list'),

    url(r'^tasks/(?P<value>[0-9]+)/edit/$', views.TaskChange.as_view(), name='task_edit'),

    url(r'^roadmaps/create/$', views.RoadmapCreate.as_view(), name='roadmap_create'),

    url(r'^roadmaps/delete/$', views.roadmap_delete, name='roadmap_delete'),

    url(r'^roadmaps/all/$', views.roadmap_list, name='roadmap_list'),

    url(r'^roadmaps/(?P<value>[0-9]+)/tasks/$', views.roadmap_tasks, name='roadmap_tasks'),

    url(r'^roadmaps/(?P<value>[0-9]+)/statistics/$', views.RoadmapStatistics.as_view(), name='roadmap_statistics'),

    url(r'^roadmaps/generate/(?P<value>[0-9]{1,4})$', views.generate_tasks, name='generate_tasks'),

    url(r'^$', views.main, name='main'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
