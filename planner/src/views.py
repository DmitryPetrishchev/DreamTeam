from django.shortcuts import render
from src.forms import TaskInputForm, TaskEditForm
from src.models import Task, Roadmap

def task_input_form(request):
    if request.POST:
        form = TaskInputForm(request.POST)
    else:
        form = TaskInputForm()
    if form.is_valid():
        return render(request, 'created_form.html', {'form': form})
    return render(request, 'form.html', {'form': form, 'title': 'Создание задачи'})

def task_edit_form(request):
    if request.POST:
        form = TaskEditForm(request.POST)
    else:
        form = TaskEditForm()
    if form.is_valid():
        return render(request, 'created_form.html', {'form': form})
    return render(request, 'form.html', {'form': form, 'title': 'Редактирование задачи'})
