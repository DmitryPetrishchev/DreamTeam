from datetime import date, datetime, timedelta
from random import randrange
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Count, DateField, ExpressionWrapper, F, Sum
from django.db.models.functions import ExtractYear, ExtractMonth, ExtractWeek
from django.views import View
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from isoweek import Week
import os
from src.forms import TaskCreationForm, TaskChangeForm, RoadmapCreationForm, \
                      UserCreationForm, UserChangeForm, PasswordChangeForm, \
                      LoginForm, UploadImageForm
from src.models import Task, Roadmap, Scores

@require_GET
@login_required
@transaction.atomic
def generate_tasks(request):
    roadmap = Roadmap.objects.create(user=request.user, title='Random roadmap')
    value = int(request.GET['value'])
    for i in range(value):
        title = 'Random task (%s)' % i
        year = randrange(2007, 2020)
        month = randrange(1, 13)
        day = randrange(1, 29)
        estimate = date(year, month, day)
        task = Task.objects.create(title=title, estimate=estimate, roadmap_id=roadmap.id)
        task.create_date = estimate - timedelta(days=randrange(500, 1000))
        task.save()
        if randrange(0, 2):
            task.state = 'ready'
            task.save()
            score = task.scores
            score.date = estimate - timedelta(days=randrange(0, 500))
            score.save()
    return redirect(reverse('src:main'))


class Login(View):
    http_method_names = ['get', 'post']

    def get(self, request, *args, error=False, **kwargs):
        form = LoginForm()
        return render(request, 'login.html', {
            'form': form,
            'error': error,
        })

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=email, password=password)
        if user is not None:
            if not request.POST.get('remember'):
                request.session.set_expiry(0)
            else:
                pass
            login(request, user)
            return redirect(reverse('src:main'))
        else:
            return self.get(request, error=True)


@require_GET
@login_required
def Logout(request):
    logout(request)
    return redirect(reverse('src:login'))

class Registration(View):
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        form = UserCreationForm()
        return render(request, 'registration.html', {
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            return redirect(reverse('src:login'))
        else:
            return render(request, 'registration.html', {
                'form': form,
            })


@require_GET
@login_required
def user_profile(request):
    form = UploadImageForm()
    return render(request, 'user_profile.html', {
        'user': request.user,
        'form': form,
    })

class UserChange(LoginRequiredMixin, View):
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        request.session['return_path'] = request.META.get('HTTP_REFERER', '/')
        form = UserChangeForm(instance=request.user)
        return render(request, 'user_change.html', {
            'form': form,
            'return_path': request.session['return_path'],
        })

    def post(self, request, *args, **kwargs):
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            return redirect(request.session['return_path'])
        else:
            return render(request, 'user_change.html', {
                'form': form,
                'return_path': request.session['return_path'],
            })

@require_POST
@login_required
@transaction.atomic
def upload_image(request):
    form = UploadImageForm(request.POST, request.FILES)
    if form.is_valid():
        user = request.user
        user.image = form.cleaned_data['image']
        user.save()
        return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        raise Http404('Что-то пошло не так при загрузке изображения.')

@require_POST
@login_required
@transaction.atomic
def delete_image(request):
    return_path = request.META.get('HTTP_REFERER', '/')
    try:
        value = int(request.POST.get('id', -1))
    except ValueError:
        raise Http404('Ах-хах, хакер, что ты делаешь, прекрати!')
    else:
        if value > 0:
            if value == request.user.id:
                request.user.image.delete()
                request.user.save()
            else:
                raise Http404('У Вас недостаточно прав на удаление данного изображения.')
        else:
            raise Http404('Запрос не содержит параметра "id".')
    return redirect(return_path)


class PasswordChange(LoginRequiredMixin, View):
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        request.session['return_path'] = request.META.get('HTTP_REFERER', '/')
        form = PasswordChangeForm(user=request.user)
        return render(request, 'password_change.html', {
            'form': form,
            'return_path': request.session['return_path'],
        })

    def post(self, request, *args, **kwargs):
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save()
                update_session_auth_hash(request, form.user)
            return redirect(request.session['return_path'])
        else:
            return render(request, 'password_change.html', {
                'form': form,
                'return_path': request.session['return_path'],
            })


@require_GET
@login_required
def main(request):
    return render(request, 'main.html')


class TaskCreate(LoginRequiredMixin, View):
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        form = TaskCreationForm(user=request.user)
        return render(request, 'form.html', {
            'form': form,
            'title': 'Создание задачи',
        })

    def post(self, request, *args, **kwargs):
        form = TaskCreationForm(request.POST, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            return render(request, 'success.html', {
                'title': 'Задача создана',
                'title_body': 'Задача успешно создана',
                'form': form,
            })
        else:
            return render(request, 'form.html', {
                'form': form,
                'title': 'Создание задачи',
            })


class RoadmapCreate(LoginRequiredMixin, View):
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        form = RoadmapCreationForm()
        return render(request, 'form.html', {
            'form': form,
            'title': 'Создание списка задач'
        })

    def post(self, request, *args, **kwargs):
        form = RoadmapCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                roadmap = Roadmap(user=request.user)
                form = RoadmapCreationForm(request.POST, instance=roadmap)
                form.save()
            return render(request, 'success.html', {
                'title': 'Список создан',
                'title_body': 'Список задач успешно создан',
                'form': form,
            })
        else:
            return render(request, 'form.html', {
                'form': form,
                'title': 'Создание списка задач',
            })


@require_POST
@login_required
@transaction.atomic
def task_delete(request):
    return_path = request.META.get('HTTP_REFERER', '/')
    try:
        value = int(request.POST.get('id', -1))
    except ValueError:
        raise Http404('Ах-хах, хакер, что ты делаешь, прекрати!')
    else:
        if value > 0:
            task = get_object_or_404(Task, id=value)
            if task.roadmap.user == request.user:
                task.delete()
            else:
                raise Http404('У Вас недостаточно прав на удаление данной задачи.')
        else:
            raise Http404('Запрос не содержит параметра "id".')
    return redirect(return_path)


@require_POST
@login_required
@transaction.atomic
def roadmap_delete(request):
    return_path = request.META.get('HTTP_REFERER', '/')
    try:
        value = int(request.POST.get('id', -1))
    except ValueError:
        raise Http404('Ах-хах, хакер, что ты делаешь, прекрати!')
    else:
        if value > 0:
            roadmap = get_object_or_404(Roadmap, id=value)
            if roadmap.user == request.user:
                roadmap.delete()
            else:
                raise Http404('У Вас недостаточно прав на удаление данного списка задач.')
        else:
            raise Http404('Запрос не содержит параметра "id".')
    return redirect(return_path)


@require_GET
@login_required
@transaction.atomic
def task_list(request):
    tasks = Task.objects.filter(roadmap__user=request.user).order_by('state', 'estimate')
    return render(request, 'task_list.html', {'tasks': tasks})


@require_GET
@login_required
@transaction.atomic
def roadmap_list(request):
    roadmaps = Roadmap.objects.filter(user=request.user).order_by('title')
    return render(request, 'roadmap_list.html', {'roadmaps': roadmaps})


@require_GET
@login_required
@transaction.atomic
def roadmap_tasks(request, *, value=-1):
    roadmap = get_object_or_404(Roadmap, id=value)
    if roadmap.user != request.user:
        raise Http404('У Вас недостаточно прав для просмотра данного списка задач.')
    if hasattr(roadmap, 'tasks'):
        tasks = roadmap.tasks.order_by('state', 'estimate')
    else:
        tasks = {}
    return render(request, 'task_list.html', {
        'tasks': tasks,
        'return_path': reverse('src:roadmap_list')
    })


class TaskChange(LoginRequiredMixin, View):
    http_method_names = ['get', 'post']

    def get(self, request, *args, value=-1, **kwargs):
        task = get_object_or_404(Task, id=value)
        if task.roadmap.user != request.user:
            raise Http404('У Вас недостаточно прав для редактирования данной задачи.')
        form = TaskChangeForm(user=request.user, instance=task)
        request.session['return_path'] = request.META.get('HTTP_REFERER', '/')
        return render(request, 'form.html', {
            'title': 'Редактирование задачи',
            'form': form,
            'return_path': request.session['return_path'],
        })

    def post(self, request, *args, value=-1, **kwargs):
        form = TaskChangeForm(request.POST, user=request.user)
        if form.is_valid():
            task = get_object_or_404(Task, id=value)
            if task.roadmap.user != request.user:
                raise Http404('У Вас недостаточно прав для редактирования данной задачи.')
            form = TaskChangeForm(request.POST, user=request.user, instance=task)
            with transaction.atomic():
                form.save()
            return redirect(request.session['return_path'])
        else:
            return render(request, 'form.html', {
                'title': 'Редактирование задачи',
                'form': form,
                'return_path': request.session['return_path']
            })


@require_GET
@login_required
@transaction.atomic
def roadmap_statistics(request, *, value=-1):
    roadmap = get_object_or_404(Roadmap, id=value)
    if roadmap.user != request.user:
        raise Http404('У Вас недостаточно прав на просмотр статистики по данному списку задач.')
    if hasattr(roadmap, 'tasks'):
        tasks = roadmap.tasks.only('create_date').annotate(
            year=ExtractYear('create_date'),
            week=ExtractWeek('create_date')
        )
        scores = Scores.objects.filter(task__in=tasks).only(
            'date',
            'points'
        ).annotate(
            year=ExtractYear(
                ExpressionWrapper(F('date'), output_field=DateField())
            ),
            month=ExtractMonth(
                ExpressionWrapper(F('date'), output_field=DateField())
            ),
            week=ExtractWeek(
                ExpressionWrapper(F('date'), output_field=DateField())
            )
        )
        created_tasks = tasks.values('year', 'week').annotate(created=Count('week'))
        solved_tasks = scores.values('year', 'week').annotate(solved=Count('week'))
        points = scores.values('year', 'month').annotate(
            points=Sum('points')
        ).order_by('year', 'month')

        table1 = {}
        for tasks in (created_tasks, solved_tasks):
            for task in tasks:
                if not table1.get(task.get('year')):
                    table1[task.get('year')] = {}
                if not table1[task.get('year')].get(task.get('week')):
                    start_date = Week(task.get('year'), task.get('week')).monday()
                    end_date = start_date + timedelta(days=6)
                    dates = str(start_date) + ' / ' + str(end_date)
                    table1[task.get('year')][task.get('week')] = {
                        'dates': dates,
                        'created': 0,
                        'solved': 0
                    }
                if task.get('created'):
                    table1[task.get('year')][task.get('week')]['created'] = task.get('created')
                elif task.get('solved'):
                    table1[task.get('year')][task.get('week')]['solved'] = task.get('solved')

        table2 = {}
        for row in points:
            if not table2.get(row.get('year')):
                table2[row.get('year')] = []
            data = {
                'month': row.get('month'),
                'points': row.get('points')
            }
            table2[row.get('year')].append(data)
    else:
        table1 = {}
        table2 = {}

    return render(request, 'roadmap_statistics.html', {
        'data': table1,
        'points': table2,
        'return_path': reverse('src:roadmap_list')
    })
