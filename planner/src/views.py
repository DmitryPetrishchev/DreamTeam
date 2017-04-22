from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from src.forms import TaskForm, RoadmapForm
from src.models import Task, Roadmap

def main(request):
    return render(request, 'main.html')

def task_create(request):
    if request.POST:
        form = TaskForm(request.POST)
    else:
        form = TaskForm()
    if form.is_valid():
        form.save()
        return render(request, 'success.html', {
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
            'form': form,
            'title': 'Создание списка',
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
        raise Http404("Список задач с id=%s не существует" % value)
    else:
        roadmap.delete()
    return redirect(return_path)

def task_list(request):
    tasks = Task.objects.order_by('state', 'estimate')
    return render(request, 'task_list.html', {'tasks': tasks})

def roadmap_list(request):
    roadmaps = Roadmap.objects.all()
    return render(request, 'roadmap_list.html', {'roadmaps': roadmaps})

def roadmap_tasks(request, value):
    tasks = Roadmap.objects.get(id=value).tasks.all()
    return render(request, 'task_list.html', {
        'tasks': tasks,
        'return_path': reverse('src:roadmap_list'),
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
            'form': form,
            'title': 'Редактирование задачи',
            'return_path': request.session['return_path']
        })
