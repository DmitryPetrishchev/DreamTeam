from django.shortcuts import render
from src.forms import TaskInputForm, TaskEditForm

def task_input_form(request):
    if request.POST:
        form = TaskInputForm(request.POST)
    else:
        form = TaskInputForm()
    return render(request, 'form.html', {'form': form, 'title': 'Создание задачи'})

def task_edit_form(request):
    if request.POST:
        form = TaskEditForm(request.POST)
    else:
        form = TaskEditForm()
    return render(request, 'form.html', {'form': form, 'title': 'Редактирование задачи'})
