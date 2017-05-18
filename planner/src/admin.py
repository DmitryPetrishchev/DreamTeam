from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from src.models import Task, Roadmap, Scores, User

admin.site.register(Task)
admin.site.register(Roadmap)
admin.site.register(Scores)
admin.site.register(User, UserAdmin)
