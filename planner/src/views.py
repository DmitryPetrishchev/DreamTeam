from calendar import monthrange
from datetime import date, datetime, timedelta
from django.core.urlresolvers import reverse
from django.db.models import Max, Min, Sum
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, Http404
from src.forms import TaskForm, RoadmapForm
from src.models import Task, Roadmap, Scores

def main(request):
    return render(request, 'main.html')

def task_create(request):
    if request.POST:
        form = TaskForm(request.POST, hidden=True)
    else:
        form = TaskForm(hidden=True)
    if form.is_valid():
        form.save()
        return render(request, 'success.html', {
            'title': 'Задача создана',
            'form': form,
            'text_head': 'Задача успешно создана',
        })
    return render(request, 'form.html', {'form': form, 'title': 'Создание задачи'})

def roadmap_create(request):
    if request.POST:
        form = RoadmapForm(request.POST)
    else:
        form = RoadmapForm()
    if form.is_valid():
        form.save()
        return render(request, 'success.html', {
            'title': 'Список создан',
            'form': form,
            'text_head': 'Список задач успешно создан',
        })
    return render(request, 'form.html', {'form': form, 'title': 'Создание списка задач'})

def task_delete(request, value=None):
    return_path = request.META.get('HTTP_REFERER', '/')
    try:
        task = Task.objects.get(id=value)
    except Task.DoesNotExist:
        raise Http404("Задача с id=%s не существует" % value)
    else:
        task.delete()
    return redirect(return_path)

def roadmap_delete(request, value=None):
    return_path = request.META.get('HTTP_REFERER', '/')
    try:
        roadmap = Roadmap.objects.get(id=value)
    except Roadmap.DoesNotExist:
        raise Http404("Списка задач с id=%s не существует" % value)
    else:
        roadmap.delete()
    return redirect(return_path)

def task_list(request):
    tasks = Task.objects.order_by('state', 'estimate')
    return render(request, 'task_list.html', {'tasks': tasks})

def roadmap_list(request):
    roadmaps = Roadmap.objects.all()
    return render(request, 'roadmap_list.html', {'roadmaps': roadmaps})

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

def roadmap_statistics(request, value=None):
    try:
        roadmap = Roadmap.objects.get(id=value)
    except Roadmap.DoesNotExist:
        raise Http404("Списка задач с id=%s не существует" % value)
    else:
        tasks = roadmap.tasks.all()
        min_date = tasks.aggregate(min_date=Min('create_date')).get('min_date')
        max_dates = tasks.aggregate(Max('create_date'), Max('estimate'))
        max_date = max(max_dates.values())
        years = {}
        for year in range(min_date.year, max_date.year + 1):
            years[year] = []
            start_date = date(year, 1, 1)
            while start_date < max_date and start_date.year == year:
                week = int(start_date.strftime('%U'))
                end_date = start_date + timedelta(days=6)
                created = tasks.filter(create_date__range=(
                    start_date,
                    end_date
                )).count()
                solved = tasks.filter(score__date__range=(
                    datetime.combine(start_date, datetime.min.time()),
                    datetime.combine(end_date, datetime.max.time())
                )).count()
                if created or solved:
                    dates = start_date.strftime('%Y-%m-%d') + ' / ' + end_date.strftime('%Y-%m-%d')
                    years[year].append({
                        'week': week,
                        'dates': dates,
                        'created': created,
                        'solved': solved
                    })
                start_date += timedelta(days=7)
        scores = {}
        for year in range(min_date.year, max_date.year + 1):
            scores[year] = []
            for month in range(1, 13):
                start_date = datetime.combine(
                    date(year, month, 1),
                    datetime.min.time())
                end_date = datetime.combine(
                    date(year, month, monthrange(year, month)[1]),
                    datetime.max.time())
                points = tasks.filter(score__date__range=(
                    start_date,
                    end_date
                )).aggregate(sum=Sum('score__points')).get('sum')
                if points:
                    scores[year].append({
                        'month': str(year) + '-' + str(month),
                        'points': points
                    })
        return render(request, 'roadmap_statistics.html', {
            'years': sorted(years.items()),
            'scores': sorted(scores.items()),
            'return_path': reverse('src:roadmap_list'),
        })
