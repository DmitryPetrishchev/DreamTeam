from datetime import date, datetime, timedelta
from random import randrange
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Count, DateField, ExpressionWrapper, F, Sum
from django.db.models.functions import ExtractYear, ExtractMonth, ExtractWeek
from django.views import View
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from isoweek import Week
from src.forms import TaskForm, RoadmapForm, UserCreationForm, PasswordChangeForm, LoginForm
from src.models import Task, Roadmap, Scores

@require_GET
@transaction.atomic
def generate_tasks(request):
    roadmap = Roadmap(title='Random roadmap')
    roadmap.save()
    value = int(request.GET['value'])
    for i in range(value):
        title = 'Random task (%s)' % i
        year = randrange(2007, 2020)
        month = randrange(1, 13)
        day = randrange(1, 29)
        estimate = date(year, month, day)
        task = Task(title=title, estimate=estimate, roadmap_id=roadmap.id)
        task.save()
        task.create_date = estimate - timedelta(days=randrange(500, 1000))
        task.save()
        flag = randrange(0, 2)
        if flag == 1:
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
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse('src:main'))
        else:
            return self.get(request, error=True)


@require_GET
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
        return render(request, 'registration.html', {
            'form': form,
        })

class PasswordChange(View):
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

@require_http_methods(['GET', 'POST'])
def selector(request, *args, **kwargs):
    get_view = kwargs.pop('GET', None)
    post_view = kwargs.pop('POST', None)
    if request.method == 'GET' and get_view is not None:
        return get_view(request, *args, **kwargs)
    elif request.method == 'POST' and post_view is not None:
        return post_view(request, *args, **kwargs)
    raise Http404('Не найдена функция представления.')

@require_GET
def get_task_create(request):
    form = TaskForm(hidden=True)
    return render(request, 'form.html', {
        'form': form,
        'title': 'Создание задачи'
    })

@require_POST
def post_task_create(request):
    if request.POST:
        form = TaskForm(request.POST, hidden=True)
    else:
        form = TaskForm(hidden=True)
    if form.is_valid():
        with transaction.atomic():
            form.save()
        return render(request, 'success.html', {
            'title': 'Задача создана',
            'text_head': 'Задача успешно создана',
            'form': form,
        })
    return render(request, 'form.html', {
        'form': form,
        'title': 'Создание задачи'
    })


@require_GET
def get_roadmap_create(request):
    form = RoadmapForm()
    return render(request, 'form.html', {
        'form': form,
        'title': 'Создание списка задач'
    })

@require_POST
def post_roadmap_create(request):
    if request.POST:
        form = RoadmapForm(request.POST)
    else:
        form = RoadmapForm()
    if form.is_valid():
        with transaction.atomic():
            form.save()
        return render(request, 'success.html', {
            'title': 'Список создан',
            'text_head': 'Список задач успешно создан',
            'form': form
        })
    return render(request, 'form.html', {
        'form': form,
        'title': 'Создание списка задач'
    })

@require_POST
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
            task.delete()
        else:
            raise Http404('Запрос не содержит параметра "id".')
    return redirect(return_path)

@require_POST
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
            roadmap.delete()
        else:
            raise Http404('Запрос не содержит параметра "id".')
    return redirect(return_path)

@require_GET
@transaction.atomic
def task_list(request):
    tasks = Task.objects.order_by('state', 'estimate')
    return render(request, 'task_list.html', {'tasks': tasks})

@require_GET
@transaction.atomic
def roadmap_list(request):
    roadmaps = Roadmap.objects.order_by('title')
    return render(request, 'roadmap_list.html', {'roadmaps': roadmaps})

@require_GET
@transaction.atomic
def roadmap_tasks(request, *, value=-1):
    roadmap = get_object_or_404(Roadmap, id=value)
    if hasattr(roadmap, 'tasks'):
        tasks = roadmap.tasks.order_by('state', 'estimate')
    else:
        tasks = {}
    return render(request, 'task_list.html', {
        'tasks': tasks,
        'return_path': reverse('src:roadmap_list')
    })

@require_GET
@transaction.atomic
def get_task_edit(request, *, value=-1):
    task = get_object_or_404(Task, id=value)
    form = TaskForm(instance=task)
    request.session['return_path'] = request.META.get('HTTP_REFERER', '/')
    return render(request, 'form.html', {
        'title': 'Редактирование задачи',
        'form': form,
        'return_path': request.session['return_path']
    })

@require_POST
@transaction.atomic
def post_task_edit(request, *, value=-1):
    form = TaskForm(request.POST)
    if form.is_valid():
        task = get_object_or_404(Task, id=value)
        form = TaskForm(request.POST, instance=task)
        form.save()
        return redirect(request.session['return_path'])
    return render(request, 'form.html', {
        'title': 'Редактирование задачи',
        'form': form,
        'return_path': request.session['return_path']
    })

@require_GET
@transaction.atomic
def roadmap_statistics(request, *, value=-1):
    roadmap = get_object_or_404(Roadmap, id=value)
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
