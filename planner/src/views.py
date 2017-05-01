from datetime import date, timedelta
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Count, DateField, ExpressionWrapper, F, Sum
from django.db.models.functions import ExtractYear, ExtractMonth, ExtractWeek
from django.views.decorators.http import require_http_methods, require_GET
from django.shortcuts import render, redirect
from django.http import Http404
from isoweek import Week
from src.forms import TaskForm, RoadmapForm
from src.models import Task, Roadmap, Scores

@require_GET
def main(request):
    return render(request, 'main.html')

@require_http_methods(['GET', 'POST'])
@transaction.atomic
def task_create(request):
    if request.POST:
        form = TaskForm(request.POST, hidden=True)
    else:
        form = TaskForm(hidden=True)
    if form.is_valid():
        form.save()
        return render(request, 'success.html', {
            'title': 'Задача создана',
            'text_head': 'Задача успешно создана',
            'form': form,
        })
    return render(request, 'form.html', {'form': form, 'title': 'Создание задачи'})

@require_http_methods(['GET', 'POST'])
@transaction.atomic
def roadmap_create(request):
    if request.POST:
        form = RoadmapForm(request.POST)
    else:
        form = RoadmapForm()
    if form.is_valid():
        form.save()
        return render(request, 'success.html', {
            'title': 'Список создан',
            'text_head': 'Список задач успешно создан',
            'form': form,
        })
    return render(request, 'form.html', {'form': form, 'title': 'Создание списка задач'})

@require_GET
@transaction.atomic
def task_delete(request, value=None):
    return_path = request.META.get('HTTP_REFERER', '/')
    try:
        task = Task.objects.get(id=value)
    except Task.DoesNotExist:
        raise Http404("Задача с id=%s не существует" % value)
    else:
        task.delete()
    return redirect(return_path)

@require_GET
@transaction.atomic
def roadmap_delete(request, value=None):
    return_path = request.META.get('HTTP_REFERER', '/')
    try:
        roadmap = Roadmap.objects.get(id=value)
    except Roadmap.DoesNotExist:
        raise Http404("Списка задач с id=%s не существует" % value)
    else:
        roadmap.delete()
    return redirect(return_path)

@require_GET
@transaction.atomic
def task_list(request):
    tasks = Task.objects.order_by('state', 'estimate')
    return render(request, 'task_list.html', {'tasks': tasks})

@require_GET
@transaction.atomic
def roadmap_list(request):
    roadmaps = Roadmap.objects.all()
    return render(request, 'roadmap_list.html', {'roadmaps': roadmaps})

@require_GET
@transaction.atomic
def roadmap_tasks(request, value=None):
    try:
        tasks = Roadmap.objects.get(id=value).tasks.all()
    except Roadmap.DoesNotExist:
        raise Http404("Списка задач с id=%s не существует" % value)
    else:
        return render(request, 'task_list.html', {
            'tasks': tasks,
            'return_path': reverse('src:roadmap_list')
        })

@require_http_methods(['GET', 'POST'])
@transaction.atomic
def task_edit(request, value=None):
    try:
        task = Task.objects.get(id=value)
    except Task.DoesNotExist:
        raise Http404("Задача с id=%s не существует" % value)
    else:
        form = TaskForm(request.POST)
        if not request.POST:
            request.session['return_path'] = request.META.get('HTTP_REFERER', '/')
            form = TaskForm(instance=task)
        elif form.is_valid():
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
def roadmap_statistics(request, value=None):
    try:
        roadmap = Roadmap.objects.get(id=value)
    except Roadmap.DoesNotExist:
        raise Http404("Списка задач с id=%s не существует" % value)
    else:
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

        return render(request, 'roadmap_statistics.html', {
            'data': table1,
            'points': table2,
            'return_path': reverse('src:roadmap_list'),
        })
